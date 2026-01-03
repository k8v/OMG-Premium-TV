const express = require('express');
const cors = require('cors');
const { addonBuilder } = require('stremio-addon-sdk');
const PlaylistTransformer = require('./playlist-transformer');
const { catalogHandler, streamHandler } = require('./handlers');
const metaHandler = require('./meta-handler');
const EPGManager = require('./epg-manager');
const config = require('./config');
const CacheManagerFactory = require('./cache-manager');
const { renderConfigPage } = require('./views');
const PythonRunner = require('./python-runner');
const ResolverStreamManager = require('./resolver-stream-manager')();
const PythonResolver = require('./python-resolver');
const fs = require('fs');
const path = require('path');
const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Route principale - supporte à la fois l'ancien et le nouveau système
app.get('/', async (req, res) => {
    const protocol = req.headers['x-forwarded-proto'] || req.protocol;
    const host = req.headers['x-forwarded-host'] || req.get('host');
    res.send(renderConfigPage(protocol, host, req.query, config.manifest));
});

// Nouvelle route pour la configuration encodée
app.get('/:config/configure', async (req, res) => {
    try {
        const protocol = req.headers['x-forwarded-proto'] || req.protocol;
        const host = req.headers['x-forwarded-host'] || req.get('host');
        const configString = Buffer.from(req.params.config, 'base64').toString();
        const decodedConfig = Object.fromEntries(new URLSearchParams(configString));

        // Initialise le générateur Python si configuré
        if (decodedConfig.python_script_url) {
            console.log('Initialisation du Script Python Générateur depuis la configuration');
            try {
                // Télécharge le script Python s'il n'est pas déjà téléchargé
                await PythonRunner.downloadScript(decodedConfig.python_script_url);

                // Si un intervalle de mise à jour a été défini, le configurer
                if (decodedConfig.python_update_interval) {
                    console.log('Configuration de la mise à jour automatique du générateur Python');
                    PythonRunner.scheduleUpdate(decodedConfig.python_update_interval);
                }
            } catch (pythonError) {
                console.error('Erreur lors de l\'initialisation du script Python :', pythonError);
            }
        }

        res.send(renderConfigPage(protocol, host, decodedConfig, config.manifest));
    } catch (error) {
        console.error('Erreur dans la configuration :', error);
        res.redirect('/');
    }
});

// Route pour le manifeste - supporte à la fois l'ancien et le nouveau système
app.get('/manifest.json', async (req, res) => {
    try {
        const protocol = req.headers['x-forwarded-proto'] || req.protocol;
        const host = req.headers['x-forwarded-host'] || req.get('host');
        const configUrl = `${protocol}://${host}/?${new URLSearchParams(req.query)}`;
        if (req.query.resolver_update_interval) {
            configUrl += `&resolver_update_interval=${encodeURIComponent(req.query.resolver_update_interval)}`;
        }
        if (req.query.m3u && global.CacheManager.cache.m3uUrl !== req.query.m3u) {
            await global.CacheManager.rebuildCache(req.query.m3u);
        }

        const { genres } = global.CacheManager.getCachedData();
        const manifestConfig = {
            ...config.manifest,
            catalogs: [{
                ...config.manifest.catalogs[0],
                extra: [
                    {
                        name: 'genre',
                        isRequired: false,
                        options: genres
                    },
                    {
                        name: 'search',
                        isRequired: false
                    },
                    {
                        name: 'skip',
                        isRequired: false
                    }
                ]
            }],
            behaviorHints: {
                configurable: true,
                configurationURL: configUrl,
                reloadRequired: true
            }
        };
        const builder = new addonBuilder(manifestConfig);

        if (req.query.epg_enabled === 'true') {
            // Si l'URL EPG n'a pas été fournie manuellement, utiliser celle de la playlist
            const epgToUse = req.query.epg ||
                (global.CacheManager.getCachedData().epgUrls &&
                    global.CacheManager.getCachedData().epgUrls.length > 0
                    ? global.CacheManager.getCachedData().epgUrls.join(',')
                    : null);

            if (epgToUse) {
                await EPGManager.initializeEPG(epgToUse);
            }
        }
        builder.defineCatalogHandler(async (args) => catalogHandler({ ...args, config: req.query }));
        builder.defineStreamHandler(async (args) => streamHandler({ ...args, config: req.query }));
        builder.defineMetaHandler(async (args) => metaHandler({ ...args, config: req.query }));
        res.setHeader('Content-Type', 'application/json');
        res.send(builder.getInterface().manifest);
    } catch (error) {
        console.error('Erreur lors de la création du manifeste :', error);
        res.status(500).json({ error: 'Erreur interne du serveur' });
    }
});

// Nouvelle route pour le manifeste avec configuration encodée
app.get('/:config/manifest.json', async (req, res) => {
    try {
        const protocol = req.headers['x-forwarded-proto'] || req.protocol;
        const host = req.headers['x-forwarded-host'] || req.get('host');
        const configString = Buffer.from(req.params.config, 'base64').toString();
        const decodedConfig = Object.fromEntries(new URLSearchParams(configString));

        if (decodedConfig.m3u && global.CacheManager.cache.m3uUrl !== decodedConfig.m3u) {
            await global.CacheManager.rebuildCache(decodedConfig.m3u);
        }
        if (decodedConfig.resolver_script) {
            console.log('Initialisation du Script Resolver depuis la configuration');
            try {
                // Télécharge le script Resolver
                const resolverDownloaded = await PythonResolver.downloadScript(decodedConfig.resolver_script);

                // Si un intervalle de mise à jour a été défini, le configurer
                if (decodedConfig.resolver_update_interval) {
                    console.log('Configuration de la mise à jour automatique du resolver');
                    PythonResolver.scheduleUpdate(decodedConfig.resolver_update_interval);
                }
            } catch (resolverError) {
                console.error('Erreur lors de l\'initialisation du script Resolver :', resolverError);
            }
        }
        // Initialise le générateur Python si configuré
        if (decodedConfig.python_script_url) {
            console.log('Initialisation du Script Python Générateur depuis la configuration');
            try {
                // Télécharge le script Python s'il n'est pas déjà téléchargé
                await PythonRunner.downloadScript(decodedConfig.python_script_url);

                // Si un intervalle de mise à jour a été défini, le configurer
                if (decodedConfig.python_update_interval) {
                    console.log('Configuration de la mise à jour automatique du générateur Python');
                    PythonRunner.scheduleUpdate(decodedConfig.python_update_interval);
                }
            } catch (pythonError) {
                console.error('Erreur lors de l\'initialisation du script Python :', pythonError);
            }
        }

        const { genres } = global.CacheManager.getCachedData();
        const manifestConfig = {
            ...config.manifest,
            catalogs: [{
                ...config.manifest.catalogs[0],
                extra: [
                    {
                        name: 'genre',
                        isRequired: false,
                        options: genres
                    },
                    {
                        name: 'search',
                        isRequired: false
                    },
                    {
                        name: 'skip',
                        isRequired: false
                    }
                ]
            }],
            behaviorHints: {
                configurable: true,
                configurationURL: `${protocol}://${host}/${req.params.config}/configure`,
                reloadRequired: true
            }
        };

        const builder = new addonBuilder(manifestConfig);

        if (decodedConfig.epg_enabled === 'true') {
            // Si l'URL EPG n'a pas été fournie manuellement, utiliser celle de la playlist
            const epgToUse = decodedConfig.epg ||
                (global.CacheManager.getCachedData().epgUrls &&
                    global.CacheManager.getCachedData().epgUrls.length > 0
                    ? global.CacheManager.getCachedData().epgUrls.join(',')
                    : null);

            if (epgToUse) {
                await EPGManager.initializeEPG(epgToUse);
            }
        }

        builder.defineCatalogHandler(async (args) => catalogHandler({ ...args, config: decodedConfig }));
        builder.defineStreamHandler(async (args) => streamHandler({ ...args, config: decodedConfig }));
        builder.defineMetaHandler(async (args) => metaHandler({ ...args, config: decodedConfig }));

        res.setHeader('Content-Type', 'application/json');
        res.send(builder.getInterface().manifest);
    } catch (error) {
        console.error('Erreur lors de la création du manifeste :', error);
        res.status(500).json({ error: 'Erreur interne du serveur' });
    }
});

// Maintien de la route existante pour les autres points de terminaison (endpoints)
app.get('/:resource/:type/:id/:extra?.json', async (req, res, next) => {
    const { resource, type, id } = req.params;
    const extra = req.params.extra
        ? safeParseExtra(req.params.extra)
        : {};

    try {
        let result;
        switch (resource) {
            case 'stream':
                result = await streamHandler({ type, id, config: req.query });
                break;
            case 'catalog':
                result = await catalogHandler({ type, id, extra, config: req.query });
                break;
            case 'meta':
                result = await metaHandler({ type, id, config: req.query });
                break;
            default:
                next();
                return;
        }

        res.setHeader('Content-Type', 'application/json');
        res.send(result);
    } catch (error) {
        console.error('Erreur lors du traitement de la requête :', error);
        res.status(500).json({ error: 'Erreur interne du serveur' });
    }
});

// Route de téléchargement du template
app.get('/api/resolver/download-template', (req, res) => {
    const PythonResolver = require('./python-resolver');
    const fs = require('fs');

    try {
        if (fs.existsSync(PythonResolver.scriptPath)) {
            res.setHeader('Content-Type', 'text/plain');
            res.setHeader('Content-Disposition', 'attachment; filename="resolver_script.py"');
            res.sendFile(PythonResolver.scriptPath);
        } else {
            res.status(404).json({ success: false, message: 'Template non trouvé. Créez-le d\'abord avec la fonction "Créer Template".' });
        }
    } catch (error) {
        console.error('Erreur lors du téléchargement du template :', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

function cleanupTempFolder() {
    console.log('\n=== Nettoyage du dossier temp au démarrage ===');
    const tempDir = path.join(__dirname, 'temp');

    // Vérifie si le dossier temp existe
    if (!fs.existsSync(tempDir)) {
        console.log('Dossier temp non trouvé, création en cours...');
        fs.mkdirSync(tempDir, { recursive: true });
        return;
    }

    try {
        // Lit tous les fichiers dans le dossier temp
        const files = fs.readdirSync(tempDir);
        let deletedCount = 0;

        // Supprime chaque fichier
        for (const file of files) {
            try {
                const filePath = path.join(tempDir, file);
                // Vérifie s'il s'agit d'un fichier et non d'un dossier
                if (fs.statSync(filePath).isFile()) {
                    fs.unlinkSync(filePath);
                    deletedCount++;
                }
            } catch (fileError) {
                console.error(`❌ Erreur lors de la suppression du fichier ${file} :`, fileError.message);
            }
        }

        console.log(`✓ ${deletedCount} fichiers temporaires supprimés`);
        console.log('=== Nettoyage du dossier temp terminé ===\n');
    } catch (error) {
        console.error('❌ Erreur lors du nettoyage du dossier temp :', error.message);
    }
}

function safeParseExtra(extraParam) {
    try {
        if (!extraParam) return {};

        const decodedExtra = decodeURIComponent(extraParam);

        // Support pour le saut (skip) avec genre
        if (decodedExtra.includes('genre=') && decodedExtra.includes('&skip=')) {
            const parts = decodedExtra.split('&');
            const genre = parts.find(p => p.startsWith('genre=')).split('=')[1];
            const skip = parts.find(p => p.startsWith('skip=')).split('=')[1];

            return {
                genre,
                skip: parseInt(skip, 10) || 0
            };
        }

        if (decodedExtra.startsWith('skip=')) {
            return { skip: parseInt(decodedExtra.split('=')[1], 10) || 0 };
        }

        if (decodedExtra.startsWith('genre=')) {
            return { genre: decodedExtra.split('=')[1] };
        }

        if (decodedExtra.startsWith('search=')) {
            return { search: decodedExtra.split('=')[1] };
        }

        try {
            return JSON.parse(decodedExtra);
        } catch {
            return {};
        }
    } catch (error) {
        console.error('Erreur lors de l\'analyse de extra :', error);
        return {};
    }
}

// Pour le catalogue avec configuration encodée
app.get('/:config/catalog/:type/:id/:extra?.json', async (req, res) => {
    try {
        const configString = Buffer.from(req.params.config, 'base64').toString();
        const decodedConfig = Object.fromEntries(new URLSearchParams(configString));
        const extra = req.params.extra
            ? safeParseExtra(req.params.extra)
            : {};

        const result = await catalogHandler({
            type: req.params.type,
            id: req.params.id,
            extra,
            config: decodedConfig
        });

        res.setHeader('Content-Type', 'application/json');
        res.send(result);
    } catch (error) {
        console.error('Erreur lors du traitement de la requête catalogue :', error);
        res.status(500).json({ error: 'Erreur interne du serveur' });
    }
});

// Pour le flux (stream) avec configuration encodée
app.get('/:config/stream/:type/:id.json', async (req, res) => {
    try {
        const configString = Buffer.from(req.params.config, 'base64').toString();
        const decodedConfig = Object.fromEntries(new URLSearchParams(configString));

        const result = await streamHandler({
            type: req.params.type,
            id: req.params.id,
            config: decodedConfig
        });

        res.setHeader('Content-Type', 'application/json');
        res.send(result);
    } catch (error) {
        console.error('Erreur lors du traitement de la requête flux :', error);
        res.status(500).json({ error: 'Erreur interne du serveur' });
    }
});

// Pour les métadonnées (meta) avec configuration encodée
app.get('/:config/meta/:type/:id.json', async (req, res) => {
    try {
        const configString = Buffer.from(req.params.config, 'base64').toString();
        const decodedConfig = Object.fromEntries(new URLSearchParams(configString));

        const result = await metaHandler({
            type: req.params.type,
            id: req.params.id,
            config: decodedConfig
        });

        res.setHeader('Content-Type', 'application/json');
        res.send(result);
    } catch (error) {
        console.error('Erreur lors du traitement de la requête méta :', error);
        res.status(500).json({ error: 'Erreur interne du serveur' });
    }
});

// Route pour servir le fichier M3U généré
app.get('/generated-m3u', (req, res) => {
    const m3uContent = PythonRunner.getM3UContent();
    if (m3uContent) {
        res.setHeader('Content-Type', 'text/plain');
        res.send(m3uContent);
    } else {
        res.status(404).send('Fichier M3U non trouvé. Exécutez d\'abord le script Python.');
    }
});

app.post('/api/resolver', async (req, res) => {
    const { action, url, interval } = req.body;

    try {
        if (action === 'download' && url) {
            const success = await PythonResolver.downloadScript(url);
            if (success) {
                res.json({ success: true, message: 'Script resolver téléchargé avec succès' });
            } else {
                res.status(500).json({ success: false, message: PythonResolver.getStatus().lastError });
            }
        } else if (action === 'create-template') {
            const success = await PythonResolver.createScriptTemplate();
            if (success) {
                res.json({
                    success: true,
                    message: 'Template script resolver créé avec succès',
                    scriptPath: PythonResolver.scriptPath
                });
            } else {
                res.status(500).json({ success: false, message: PythonResolver.getStatus().lastError });
            }
        } else if (action === 'check-health') {
            const isHealthy = await PythonResolver.checkScriptHealth();
            res.json({
                success: isHealthy,
                message: isHealthy ? 'Script resolver valide' : PythonResolver.getStatus().lastError
            });
        } else if (action === 'status') {
            res.json(PythonResolver.getStatus());
        } else if (action === 'clear-cache') {
            PythonResolver.clearCache();
            res.json({ success: true, message: 'Cache resolver vidé' });
        } else if (action === 'schedule' && interval) {
            const success = PythonResolver.scheduleUpdate(interval);
            if (success) {
                res.json({
                    success: true,
                    message: `Mise à jour automatique configurée toutes les ${interval}`
                });
            } else {
                res.status(500).json({ success: false, message: PythonResolver.getStatus().lastError });
            }
        } else if (action === 'stopSchedule') {
            const stopped = PythonResolver.stopScheduledUpdates();
            res.json({
                success: true,
                message: stopped ? 'Mise à jour automatique arrêtée' : 'Aucune mise à jour planifiée à arrêter'
            });
        } else {
            res.status(400).json({ success: false, message: 'Action non valide' });
        }
    } catch (error) {
        console.error('Erreur API Resolver :', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

app.post('/api/rebuild-cache', async (req, res) => {
    try {
        const m3uUrl = req.body.m3u;
        if (!m3uUrl) {
            return res.status(400).json({ success: false, message: 'URL M3U requise' });
        }

        console.log('🔄 Requête de reconstruction de cache reçue');
        await global.CacheManager.rebuildCache(req.body.m3u, req.body);

        if (req.body.epg_enabled === 'true') {
            console.log('📡 Reconstruction EPG en cours...');
            const epgToUse = req.body.epg ||
                (global.CacheManager.getCachedData().epgUrls && global.CacheManager.getCachedData().epgUrls.length > 0
                    ? global.CacheManager.getCachedData().epgUrls.join(',')
                    : null);
            if (epgToUse) {
                await EPGManager.initializeEPG(epgToUse);
            }
        }

        res.json({ success: true, message: 'Cache et EPG reconstruits avec succès' });

    } catch (error) {
        console.error('Erreur lors de la reconstruction du cache :', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// Endpoint API pour les opérations sur le script Python
app.post('/api/python-script', async (req, res) => {
    const { action, url, interval } = req.body;

    try {
        if (action === 'download' && url) {
            const success = await PythonRunner.downloadScript(url);
            if (success) {
                res.json({ success: true, message: 'Script téléchargé avec succès' });
            } else {
                res.status(500).json({ success: false, message: PythonRunner.getStatus().lastError });
            }
        } else if (action === 'execute') {
            const success = await PythonRunner.executeScript();
            if (success) {
                res.json({
                    success: true,
                    message: 'Script exécuté avec succès',
                    m3uUrl: `${req.protocol}://${req.get('host')}/generated-m3u`
                });
            } else {
                res.status(500).json({ success: false, message: PythonRunner.getStatus().lastError });
            }
        } else if (action === 'status') {
            res.json(PythonRunner.getStatus());
        } else if (action === 'schedule' && interval) {
            const success = PythonRunner.scheduleUpdate(interval);
            if (success) {
                res.json({
                    success: true,
                    message: `Mise à jour automatique configurée toutes les ${interval}`
                });
            } else {
                res.status(500).json({ success: false, message: PythonRunner.getStatus().lastError });
            }
        } else if (action === 'stopSchedule') {
            const stopped = PythonRunner.stopScheduledUpdates();
            res.json({
                success: true,
                message: stopped ? 'Mise à jour automatique arrêtée' : 'Aucune mise à jour planifiée à arrêter'
            });
        } else {
            res.status(400).json({ success: false, message: 'Action non valide' });
        }
    } catch (error) {
        console.error('Erreur API Python :', error);
        res.status(500).json({ success: false, message: error.message });
    }
});
async function startAddon() {
    cleanupTempFolder();

    // Initialise CacheManager
    global.CacheManager = await CacheManagerFactory(config);

    try {
        const port = process.env.PORT || 10000;
        app.listen(port, () => {
            console.log('=============================\n');
            console.log('OMG ADDON Démarré avec succès');
            console.log('Visitez la page web pour générer la configuration du manifeste et l\'installer sur Stremio');
            console.log('Lien vers la page de configuration :', `http://localhost:${port}`);
            console.log('=============================\n');
        });
    } catch (error) {
        console.error('Échec du démarrage de l\'addon :', error);
        process.exit(1);
    }
}

startAddon();

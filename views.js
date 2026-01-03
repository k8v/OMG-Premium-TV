const fs = require('fs');
const path = require('path');
const { getViewScripts } = require('./views-scripts');

const renderConfigPage = (protocol, host, query, manifest) => {
   // Vérifie si le fichier addon-config.json existe
   const configPath = path.join(__dirname, 'addon-config.json');
   const m3uDefaultUrl = 'https://github.com/mccoy88f/OMG-Premium-TV/blob/main/tv.png?raw=true';
   const m3uIsDisabled = !fs.existsSync(configPath);

   return `
       <!DOCTYPE html>
       <html>
       <head>
           <meta charset="utf-8">
           <title>${manifest.name}</title>
           <style>
               body {
                   margin: 0;
                   padding: 0;
                   height: 100vh;
                   overflow-y: auto;
                   font-family: Arial, sans-serif;
                   color: #fff;
                   background: purple;
               }
               #background-video {
                   position: fixed;
                   right: 0;
                   bottom: 0;
                   min-width: 100%;
                   min-height: 100%;
                   width: auto;
                   height: auto;
                   z-index: -1000;
                   background: black;
                   object-fit: cover;
                   filter: blur(5px) brightness(0.5);
               }
               .content {
                   position: relative;
                   z-index: 1;
                   max-width: 800px;
                   margin: 0 auto;
                   text-align: center;
                   padding: 50px 20px;
                   background: rgba(0,0,0,0.6);
                   min-height: 100vh;
                   display: flex;
                   flex-direction: column;
                   justify-content: flex-start;
                   overflow-y: visible;
               }

               .logo {
                   width: 150px;
                   margin: 0 auto 20px;
                   display: block;
               }
               .manifest-url {
                   background: rgba(255,255,255,0.1);
                   padding: 10px;
                   border-radius: 4px;
                   word-break: break-all;
                   margin: 20px 0;
                   font-size: 12px;
               }

               .loader-overlay {
                   position: fixed;
                   top: 0;
                   left: 0;
                   width: 100%;
                   height: 100%;
                   background: rgba(0,0,0,0.8);
                   display: none;
                   justify-content: center;
                   align-items: center;
                   z-index: 2000;
                   flex-direction: column;
               }
               
               .loader {
                   border: 6px solid #3d2a56;
                   border-radius: 50%;
                   border-top: 6px solid #8A5AAB;
                   width: 50px;
                   height: 50px;
                   animation: spin 1s linear infinite;
                   margin-bottom: 20px;
               }
               
               .loader-message {
                   color: white;
                   font-size: 18px;
                   text-align: center;
                   max-width: 80%;
               }
               
               @keyframes spin {
                   0% { transform: rotate(0deg); }
                   100% { transform: rotate(360deg); }
               }
               
               .config-form {
                   text-align: left;
                   background: rgba(255,255,255,0.1);
                   padding: 20px;
                   border-radius: 4px;
                   margin-top: 30px;
               }
               .config-form label {
                   display: block;
                   margin: 10px 0 5px;
                   color: #fff;
               }
               .config-form input[type="text"],
               .config-form input[type="url"],
               .config-form input[type="password"],
               .config-form input[type="file"] {
                   width: 100%;
                   padding: 8px;
                   margin-bottom: 10px;
                   border-radius: 4px;
                   border: 1px solid #666;
                   background: #333;
                   color: white;
               }
               .buttons {
                   margin: 30px 0;
                   display: flex;
                   justify-content: center;
                   gap: 20px;
               }
               button {
                   background: #8A5AAB;
                   color: white;
                   border: none;
                   padding: 12px 24px;
                   border-radius: 4px;
                   cursor: pointer;
                   font-size: 16px;
               }
               .bottom-buttons {
                   margin-top: 20px;
                   display: flex;
                   justify-content: center;
                   gap: 20px;
               }
               .toast {
                   position: fixed;
                   top: 20px;
                   right: 20px;
                   background: #4CAF50;
                   color: white;
                   padding: 15px 30px;
                   border-radius: 4px;
                   display: none;
               }
               input[type="submit"] {
                   background: #8A5AAB;
                   color: white;
                   border: none;
                   padding: 12px 24px;
                   border-radius: 4px;
                   cursor: pointer;
                   font-size: 16px;
                   width: 100%;
                   margin-top: 20px;
               }
               .advanced-settings {
                   background: rgba(255,255,255,0.05);
                   border: 1px solid #666;
                   border-radius: 4px;
                   padding: 10px;
                   margin-top: 10px;
               }
               .advanced-settings-header {
                   cursor: pointer;
                   display: flex;
                   justify-content: space-between;
                   align-items: center;
                   color: #fff;
               }
               .advanced-settings-content {
                   display: none;
                   padding-top: 10px;
               }
               .advanced-settings-content.show {
                   display: block;
               }
               #confirmModal {
                   display: none;
                   position: fixed;
                   top: 0;
                   left: 0;
                   width: 100%;
                   height: 100%;
                   background: rgba(0,0,0,0.8);
                   z-index: 1000;
                   justify-content: center;
                   align-items: center;
               }
               #confirmModal > div {
                   background: #333;
                   padding: 30px;
                   border-radius: 10px;
                   text-align: center;
                   color: white;
               }
               #confirmModal button {
                   margin: 0 10px;
               }
               a {
                   color: #8A5AAB;
                   text-decoration: none;
               }
               a:hover {
                   text-decoration: underline;
               }
           </style>
       </head>
       <body>
           <video autoplay loop muted id="background-video">
               <source src="https://static.vecteezy.com/system/resources/previews/001/803/236/mp4/no-signal-bad-tv-free-video.mp4" type="video/mp4">
               Votre navigateur ne supporte pas la balise vidéo.
           </video>

           <div class="content">
               <img class="logo" src="${manifest.logo}" alt="logo">
               <h1>${manifest.name} <span style="font-size: 16px; color: #aaa;">v${manifest.version}</span></h1>

               
               <div class="manifest-url">
                   <strong>URL Manifest:</strong><br>
                   ${protocol}://${host}/manifest.json?${new URLSearchParams(query)}
               </div>

               <div class="buttons">
                   <button onclick="copyManifestUrl()">COPIER L'URL DU MANIFEST</button>
                   <button onclick="installAddon()">INSTALLER SUR STREMIO</button>
               </div>
               
               <div class="config-form">
                   <h2>Générer la Configuration</h2>
                   <form id="configForm" onsubmit="updateConfig(event)">
                       <label>URL M3U :</label>
                       <input type="text" name="m3u" 
                              value="${m3uIsDisabled ? m3uDefaultUrl : (query.m3u || '')}" 
                              ${m3uIsDisabled ? 'readonly' : ''} 
                              placeholder="https://exemple.com/playlist1.m3u,https://exemple.com/playlist2.m3u"
                              required>
                       <small style="color: #999; display: block; margin-top: 5px;">
                           💡 Vous pouvez insérer plusieurs URL M3U en les séparant par une virgule (,)
                       </small>
                       
                       <label>URL EPG :</label>
                       <input type="text" name="epg" 
                              value="${query.epg || ''}"
                              placeholder="https://exemple.com/epg1.xml,https://exemple.com/epg2.xml">
                       <small style="color: #999; display: block; margin-top: 5px;">
                           💡 Vous pouvez insérer plusieurs URL EPG en les séparant par une virgule (,)
                       </small>
                       
                       <label>
                           <input type="checkbox" name="epg_enabled" ${query.epg_enabled === 'true' ? 'checked' : ''}>
                           Activer l'EPG
                       </label>

                       <label>Langue des Chaînes :</label>
                       <select name="language" style="width: 100%; padding: 8px; margin-bottom: 10px; border-radius: 4px; border: 1px solid #666; background: #333; color: white;">
                           <option value="Italiano" ${(query.language || 'Français') === 'Italiano' ? 'selected' : ''}>Italiano</option>
                           <option value="English" ${query.language === 'English' ? 'selected' : ''}>English</option>
                           <option value="Español" ${query.language === 'Español' ? 'selected' : ''}>Español</option>
                           <option value="Français" ${(query.language || 'Français') === 'Français' ? 'selected' : ''}>Français</option>
                           <option value="Deutsch" ${query.language === 'Deutsch' ? 'selected' : ''}>Deutsch</option>
                           <option value="Português" ${query.language === 'Português' ? 'selected' : ''}>Português</option>
                           <option value="Nederlands" ${query.language === 'Nederlands' ? 'selected' : ''}>Nederlands</option>
                           <option value="Polski" ${query.language === 'Polski' ? 'selected' : ''}>Polski</option>
                           <option value="Русский" ${query.language === 'Русский' ? 'selected' : ''}>Русский</option>
                           <option value="العربية" ${query.language === 'العربية' ? 'selected' : ''}>العربية</option>
                           <option value="中文" ${query.language === '中文' ? 'selected' : ''}>中文</option>
                           <option value="日本語" ${query.language === '日本語' ? 'selected' : ''}>日本語</option>
                           <option value="한국어" ${query.language === '한국어' ? 'selected' : ''}>한국어</option>
                       </select>

                       <div class="advanced-settings">
                           <div class="advanced-settings-header" onclick="toggleAdvancedSettings()">
                               <strong>Paramètres Avancés</strong>
                               <span id="advanced-settings-toggle">▼</span>
                           </div>
                           <div class="advanced-settings-content" id="advanced-settings-content">
                               <label>URL Proxy :</label>
                               <input type="url" name="proxy" value="${query.proxy || ''}">
                               
                               <label>Mot de passe Proxy :</label>
                               <input type="password" name="proxy_pwd" value="${query.proxy_pwd || ''}">
                               
                               <label>
                                   <input type="checkbox" name="force_proxy" ${query.force_proxy === 'true' ? 'checked' : ''}>
                                   Forcer le Proxy
                               </label>

                               <label>Suffixe d'ID :</label>
                               <input type="text" name="id_suffix" value="${query.id_suffix || ''}" placeholder="Exemple : fr">

                               <label>Chemin du fichier remapper :</label>
                               <input type="text" name="remapper_path" value="${query.remapper_path || ''}" placeholder="Exemple : https://raw.githubusercontent.com/...">

                               <label>Intervalle de mise à jour de la Playlist :</label>
                               <input type="text" name="update_interval" value="${query.update_interval || '12:00'}" placeholder="HH:MM (défaut 12:00)">
                               <small style="color: #999;">Format HH:MM (ex. 1:00 ou 01:00), défaut 12:00</small>
                               
                               <label>URL du Script Resolver Python :</label>
                               <input type="url" name="resolver_script" value="${query.resolver_script || ''}">
                               
                               <label>
                                   <input type="checkbox" name="resolver_enabled" ${query.resolver_enabled === 'true' ? 'checked' : ''}>
                                   Activer le Resolver Python
                               </label>
                               
                           </div>
                       </div>
                       <input type="hidden" name="python_script_url" id="hidden_python_script_url" value="${query.python_script_url || ''}">
                       <input type="hidden" name="python_update_interval" id="hidden_python_update_interval" value="${query.python_update_interval || ''}">
                       <input type="hidden" name="resolver_update_interval" id="hidden_resolver_update_interval" value="${query.resolver_update_interval || ''}">
                       <input type="submit" value="Générer la Configuration">
                   </form>

                   <div class="bottom-buttons">
                       <button onclick="backupConfig()">SAUVEGARDER CONFIG</button>
                       <input type="file" id="restoreFile" accept=".json" style="display:none;" onchange="restoreConfig(event)">
                       <button onclick="document.getElementById('restoreFile').click()">RESTAURER CONFIG</button>
                   </div>
                   <div style="margin-top: 15px; background: rgba(255,255,255,0.1); padding: 1px; border-radius: 4px;">
                       <ul style="text-align: center; margin-top: 10px;">
                           <p>N'oubliez pas de générer la configuration avant d'effectuer une sauvegarde</p>
                       </ul>
                   </div>
               </div>
               
               <div class="config-form" style="margin-top: 30px;">
                   <div class="advanced-settings">
                       <div class="advanced-settings-header" onclick="togglePythonSection()">
                           <strong>Générer une Playlist via Script Python</strong>
                           <span id="python-section-toggle">▼</span>
                       </div>
                       <div class="advanced-settings-content" id="python-section-content">
                           <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 4px; margin-bottom: 20px; margin-top: 15px;">
                               <p><strong>Cette fonction permet de :</strong></p>
                               <ul style="text-align: left;">
                                   <li>Télécharger un script Python depuis une URL</li>
                                   <li>L'exécuter à l'intérieur du container Docker</li>
                                   <li>Utiliser le fichier M3U généré comme source</li>
                               </ul>
                               <p><strong>Note :</strong> L'URL doit pointer vers un script Python qui génère un fichier M3U.</p>
                           </div>
            
                           <div id="pythonForm">
                               <label>URL du Script Python :</label>
                               <input type="url" id="pythonScriptUrl" placeholder="https://exemple.com/script.py">
                
                               <div style="display: flex; gap: 10px; margin-top: 15px;">
                                   <button onclick="downloadPythonScript()" style="flex: 1;">TÉLÉCHARGER</button>
                                   <button onclick="executePythonScript()" style="flex: 1;">EXÉCUTER</button>
                                   <button onclick="checkPythonStatus()" style="flex: 1;">ÉTAT</button>
                               </div>
                
                               <div style="margin-top: 15px;">
                                   <h4>Mise à jour Automatique</h4>
                                   <div style="display: flex; gap: 10px; align-items: center;">
                                       <input type="text" id="updateInterval" placeholder="HH:MM (ex. 12:00)" style="flex: 2;">
                                       <button onclick="scheduleUpdates()" style="flex: 1;">PLANIFIER</button>
                                       <button onclick="stopScheduledUpdates()" style="flex: 1;">ARRÊTER</button>
                                   </div>
                                   <small style="color: #999; display: block; margin-top: 5px;">
                                       Format : HH:MM (ex. 12:00 pour 12 heures, 1:00 pour 1 heure, 0:30 pour 30 minutes)
                                   </small>
                               </div>
                
                               <div id="pythonStatus" style="margin-top: 15px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 4px; display: none;">
                                   <h3>État du Script Python</h3>
                                   <div id="pythonStatusContent"></div>
                               </div>
                
                               <div id="generatedM3uUrl" style="margin-top: 15px; background: rgba(0,255,0,0.1); padding: 10px; border-radius: 4px; display: none;">
                                   <h3>URL de la Playlist Générée</h3>
                                   <div id="m3uUrlContent"></div>
                                   <button onclick="useGeneratedM3u()" style="width: 100%; margin-top: 10px;">UTILISER CETTE PLAYLIST</button>
                               </div>
                           </div>
                       </div>
                   </div>
               </div>

               <!-- Nouvelle section pour le Resolver Python -->
               <div class="config-form" style="margin-top: 30px;">
                   <div class="advanced-settings">
                       <div class="advanced-settings-header" onclick="toggleResolverSection()">
                           <strong>Resolver Python pour Streams</strong>
                           <span id="resolver-section-toggle">▼</span>
                       </div>
                       <div class="advanced-settings-content" id="resolver-section-content">
                           <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 4px; margin-bottom: 20px; margin-top: 15px;">
                               <p><strong>Qu'est-ce que le Resolver Python ?</strong></p>
                               <p>Le Resolver Python vous permet de :</p>
                               <ul style="text-align: left;">
                                   <li>Résoudre dynamiquement les URL de streaming</li>
                                   <li>Ajouter des jetons d'authentification aux flux</li>
                                   <li>Gérer les API protégées des fournisseurs</li>
                                   <li>Personnaliser les requêtes avec des en-têtes spécifiques</li>
                               </ul>
                               <p><strong>Note :</strong> Nécessite un script Python implémentant la fonction <code>resolve_link</code>.</p>
                           </div>
                       
                           <div id="resolverForm">
                       
                               <div style="display: flex; gap: 10px; margin-top: 15px;">
                                   <button onclick="downloadResolverScript()" style="flex: 1;">TÉLÉCHARGER</button>
                                   <button onclick="createResolverTemplate()" style="flex: 1;">CRÉER TEMPLATE</button>
                                   <button onclick="checkResolverHealth()" style="flex: 1;">VÉRIFIER</button>
                               </div>
                       
                               <div style="margin-top: 15px;">
                                   <h4>Gestion du Cache et Mises à jour</h4>
                                   <div style="display: flex; gap: 10px; align-items: center;">
                                       <input type="text" id="resolverUpdateInterval" placeholder="HH:MM (ex. 12:00)" style="flex: 2;">
                                       <button onclick="scheduleResolverUpdates()" style="flex: 1;">PLANIFIER</button>
                                       <button onclick="stopResolverUpdates()" style="flex: 1;">ARRÊTER</button>
                                       <button onclick="clearResolverCache()" style="flex: 1;">VIDER CACHE</button>
                                   </div>
                                   <small style="color: #999; display: block; margin-top: 5px;">
                                       Format : HH:MM (ex. 12:00 pour 12 heures, 1:00 pour 1 heure, 0:30 pour 30 minutes)
                                   </small>
                               </div>
                       
                               <div id="resolverStatus" style="margin-top: 15px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 4px; display: none;">
                                   <h3>État du Resolver Python</h3>
                                   <div id="resolverStatusContent"></div>
                               </div>
                           </div>
                       </div>
                   </div>
               </div>

               <div style="margin-top: 30px; text-align: center; font-size: 14px; color: #ccc;">
                   <p>Addon créé avec passion par McCoy88f - <a href="https://github.com/mccoy88f/OMG-Premium-TV" target="_blank">Dépôt GitHub</a></p>
                   
                   <h3 style="margin-top: 20px;">Soutenez ce projet !</h3>
                   
                   <div style="margin-top: 15px;">
                       <a href="https://www.buymeacoffee.com/mccoy88f" target="_blank">
                           <img src="https://img.buymeacoffee.com/button-api/?text=Offrez-moi une bière&emoji=🍺&slug=mccoy88f&button_colour=FFDD00&font_colour=000000&font_family=Bree&outline_colour=000000&coffee_colour=ffffff" alt="Buy Me a Coffee" style="max-width: 300px; margin: 0 auto;"/>
                       </a>
                   </div>
                   
                   <p style="margin-top: 15px;">
                       <a href="https://paypal.me/mccoy88f?country.x=IT&locale.x=it_IT" target="_blank">Vous pouvez aussi m'offrir une bière via PayPal 🍻</a>
                   </p>
                   
                   <div style="margin-top: 30px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 4px;">
                       <strong>ATTENTION !</strong>
                       <ul style="text-align: center; margin-top: 10px;">
                           <p>Je ne suis pas responsable de l'usage illicite de cet addon.</p>
                           <p>Vérifiez et respectez la législation en vigueur dans votre pays !</p>
                       </ul>
                   </div>
               </div>
               
               <div id="confirmModal">
                   <div>
                       <h2>Confirmer l'Installation</h2>
                       <p>Avez-vous déjà généré la configuration ?</p>
                       <div style="margin-top: 20px;">
                           <button onclick="cancelInstallation()" style="background: #666;">Retour</button>
                           <button onclick="proceedInstallation()" style="background: #8A5AAB;">Procéder</button>
                       </div>
                   </div>
               </div>
               
               <div id="toast" class="toast">URL Copiée !</div>
               
               <script>
                   ${getViewScripts(protocol, host)}
               </script>
           </div>
           <div id="loaderOverlay" class="loader-overlay">
               <div class="loader"></div>
               <div id="loaderMessage" class="loader-message">Opération en cours...</div>
           </div>
       </body>
       </html>
   `;
};

module.exports = {
    renderConfigPage
};

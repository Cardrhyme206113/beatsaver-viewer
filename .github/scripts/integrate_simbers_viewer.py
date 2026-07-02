from pathlib import Path
import re

ROOT = Path('.')

def read(path):
    return (ROOT / path).read_text(encoding='utf-8')

def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def replace_exact(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing expected block: {label}')
    return text.replace(old, new, 1)

# ---------------------------------------------------------------------------
# Viewer shell: remove branding/start overlay hooks and add integration pieces.
# ---------------------------------------------------------------------------
path = 'src/index.html'
text = read(path)
text = text.replace('<title>BeatSaver Viewer</title>', '<title>Simplified Sabers Viewer</title>', 1)
text = text.replace('    <link rel="shortcut icon" href="assets/img/favicon.png" type="image/x-icon">\n', '', 1)
text = text.replace('    <link rel="icon" href="assets/img/favicon.png" type="image/x-icon">\n', '', 1)
text = replace_exact(
    text,
    '  <head>\n    <title>Simplified Sabers Viewer</title>',
    '  <head>\n    <title>Simplified Sabers Viewer</title>\n    <meta charset="utf-8">\n    <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
    'viewer meta tags'
)
text = text.replace('      iframe-url\n', '', 1)
text = text.replace('      search\n', '', 1)
text = text.replace('      user-gesture\n', '      high-resolution-renderer\n      simbers-bridge\n      user-gesture\n', 1)
text = text.replace('      vr-mode-ui="enabled: false"\n      tutorial-2d>', '      vr-mode-ui="enabled: false">', 1)
text = text.replace("    {% include './templates/ga.html' %}\n\n", '', 1)
text = re.sub(
    r'\n    <div id="search"></div>.*?</div>\n  </body>',
    '\n  </body>',
    text,
    count=1,
    flags=re.S,
)
write(path, text)

# ---------------------------------------------------------------------------
# Remove visible viewer logos and unneeded preloaded logo models/textures.
# ---------------------------------------------------------------------------
path = 'src/templates/stage.html'
text = read(path)
text, count = re.subn(
    r'\n  <a-entity id="logo".*?</a-entity>\n',
    '\n',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit('Stage logo block not found')
write(path, text)

path = 'src/templates/controls.html'
text = read(path)
text = text.replace('  <a id="logo" href="https://supermedium.com" title="Made by Supermedium, the browser for the VR Internet."><img src="assets/img/logo.png"></a>\n\n', '', 1)
text = re.sub(r'\n<a href="https://github\.com/supermedium/beatsaver-viewer".*$', '\n', text, count=1, flags=re.S)
text = text.replace('''      <ul id="controlsModes">
        <li data-mode="Standard">Standard</li>
        <li data-mode="NoArrows">NoArrows</li>
        <li data-mode="OneSaber">OneSaber</li>
        <li data-mode="Lawless">Lawless</li>
        <li data-mode="Lightshow">Lightshow</li>
      </ul>''', '''      <ul id="controlsModes">
        <li data-mode="Standard">Standard</li>
        <li data-mode="NoArrows">NoArrows</li>
        <li data-mode="OneSaber">OneSaber</li>
        <li data-mode="90Degree">90Degree</li>
        <li data-mode="360Degree">360Degree</li>
      </ul>''', 1)
text = re.sub(r'\n      <div id="searchToggle">.*?</div>', '', text, count=1, flags=re.S)
write(path, text)

path = 'src/assets.html'
text = read(path)
for line in (
    '<a-asset-item id="logoBackObj" src="assets/models/logoback.obj"></a-asset-item>\n',
    '<a-asset-item id="logoObj" src="assets/models/logo.obj"></a-asset-item>\n',
    '<a-asset-item id="logoGlowObj" src="assets/models/logoglow.obj"></a-asset-item>\n',
    '<img id="logotexImg" src="assets/img/logotex.png">\n',
):
    text = text.replace(line, '', 1)
write(path, text)

# ---------------------------------------------------------------------------
# Remove the large CLICK ANYWHERE TO PLAY card. Loading/error card remains.
# ---------------------------------------------------------------------------
path = 'src/templates/loading.html'
text = read(path)
text = text.replace(
    'bind__animation__scale="enabled: challenge.isLoading || !hasReceivedUserGesture && !challenge.hasLoadError"',
    'bind__animation__scale="enabled: challenge.isLoading || isSongBufferProcessing"',
    1,
)
text = text.replace(
    'bind__visible="challenge.isLoading || !hasReceivedUserGesture || challenge.hasLoadError"',
    'bind__visible="challenge.isLoading || isSongBufferProcessing || challenge.hasLoadError"',
    1,
)
text, count = re.subn(
    r'\n    <a-entity\n      id="loadingGestureButton".*?</a-entity>\n',
    '\n',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit('Gesture button block not found')
write(path, text)

# ---------------------------------------------------------------------------
# State: autoplay by default and honour requested mode/difficulty.
# ---------------------------------------------------------------------------
path = 'src/state/index.js'
text = read(path)
text = text.replace("  image: 'assets/img/logo.png',", "  image: '',", 1)
text = replace_exact(
    text,
    "const isSafari = navigator.userAgent.toLowerCase().indexOf('safari') !== -1 &&\n                  navigator.userAgent.toLowerCase().indexOf('chrome') === -1;",
    "const isSafari = navigator.userAgent.toLowerCase().indexOf('safari') !== -1 &&\n                  navigator.userAgent.toLowerCase().indexOf('chrome') === -1;\nconst autoPlay = AFRAME.utils.getUrlParameter('autoplay') !== 'false';",
    'autoplay constant'
)
text = text.replace('    hasReceivedUserGesture: false,', '    hasReceivedUserGesture: autoPlay,', 1)
old = '''    challengeloadend: (state, payload) => {
      beatmaps = payload.beatmaps;
      difficulties = payload.difficulties;

      state.challenge.audio = payload.audio;
      state.challenge.author = payload.info._levelAuthorName;

      const mode = state.challenge.mode = payload.beatmaps.Standard
        ? 'Standard'
        : Object.keys(payload.beatmaps)[0];
      state.challenge.difficulties = difficulties[mode];

      if (!state.challenge.difficulty || !payload.beatmaps[mode][state.challenge.difficulty]) {
        state.challenge.difficulty = payload.difficulty;
      }

      state.challenge.id = payload.isDragDrop ? '' : payload.id;
      if (payload.image) {
        state.challenge.image = payload.image;
      }
      state.challenge.isLoading = false;
      state.challenge.songName = payload.info._songName;
      state.challenge.songNameShort = truncate(payload.info._songName, 18);
      state.challenge.songNameMedium = truncate(payload.info._songName, 30);

      state.challenge.songSubName = payload.info._songSubName || payload.info._songAuthorName;
      state.challenge.songSubNameShort = truncate(state.challenge.songSubName, 21);

      document.title = `BeatSaver Viewer | ${payload.info._songName}`;
    },'''
new = '''    challengeloadend: (state, payload) => {
      beatmaps = payload.beatmaps || {};
      difficulties = payload.difficulties || {};

      const availableModes = Object.keys(beatmaps).filter(mode =>
        beatmaps[mode] && Object.keys(beatmaps[mode]).length
      );
      const requestedMode = payload.mode || AFRAME.utils.getUrlParameter('mode');
      const mode = requestedMode && beatmaps[requestedMode]
        ? requestedMode
        : (beatmaps.Standard ? 'Standard' : availableModes[0]);
      if (!mode) { throw new Error('Map contains no playable characteristics.'); }

      state.challenge.audio = payload.audio;
      state.challenge.author = payload.info._levelAuthorName || '';
      state.challenge.mode = mode;
      state.challenge.difficulties = difficulties[mode] || [];

      const requestedDifficulty = payload.difficulty || AFRAME.utils.getUrlParameter('difficulty');
      const fallbackDifficulty = state.challenge.difficulties.length
        ? state.challenge.difficulties[state.challenge.difficulties.length - 1]._difficulty
        : Object.keys(beatmaps[mode])[0];
      state.challenge.difficulty = requestedDifficulty && beatmaps[mode][requestedDifficulty]
        ? requestedDifficulty
        : fallbackDifficulty;

      state.challenge.id = payload.isDragDrop ? '' : payload.id;
      state.challenge.image = payload.image || '';
      state.challenge.hasLoadError = false;
      state.challenge.loadErrorText = '';
      state.challenge.isLoading = false;
      state.challenge.songName = payload.info._songName || 'Generated Map';
      state.challenge.songNameShort = truncate(state.challenge.songName, 18);
      state.challenge.songNameMedium = truncate(state.challenge.songName, 30);

      state.challenge.songSubName = payload.info._songSubName || payload.info._songAuthorName || '';
      state.challenge.songSubNameShort = truncate(state.challenge.songSubName, 21);

      document.title = `Simplified Sabers Viewer | ${state.challenge.songName}`;
    },'''
text = replace_exact(text, old, new, 'challenge load state handler')
write(path, text)

# ---------------------------------------------------------------------------
# ZIP loader: robust Info.dat casing, modes, difficulties and in-memory bridge.
# ---------------------------------------------------------------------------
path = 'src/components/zip-loader.js'
text = read(path)
text = text.replace('      beatmaps: {Standard: {}},\n      beatSpeeds: {Standard: {}},\n      difficulties: {Standard: []},', '      beatmaps: {},\n      beatSpeeds: {},\n      difficulties: {},', 1)
text = text.replace("      if (filename.endsWith('info.dat')) {", "      if (filename.toLowerCase().endsWith('info.dat')) {", 1)
text = replace_exact(
    text,
    '    // See whether we need mapping extensions (per difficulty).\n    const customData = event.info._customData;',
    "    if (!event.info || !event.info._difficultyBeatmapSets) {\n      throw new Error('Info.dat is missing or does not contain difficulty sets.');\n    }\n\n    // See whether we need mapping extensions (per difficulty).\n    const customData = event.info._customData;",
    'Info.dat validation'
)
text = text.replace('      const diffBeatmaps = set._difficultyBeatmaps.sort(d => d._difficultyRank);', '      const diffBeatmaps = set._difficultyBeatmaps.slice().sort((a, b) => a._difficultyRank - b._difficultyRank);', 1)
old = '''    // Default to hardest of first beatmap.
    if (!event.difficulty) {
      event.difficulty = this.data.difficulty || event.difficulties.Standard[0]._difficulty;
    }
'''
new = '''    const availableModes = Object.keys(event.beatmaps).filter(mode =>
      event.beatmaps[mode] && Object.keys(event.beatmaps[mode]).length
    );
    event.mode = this.data.mode && event.beatmaps[this.data.mode]
      ? this.data.mode
      : (event.beatmaps.Standard ? 'Standard' : availableModes[0]);
    if (!event.mode) { throw new Error('Map contains no playable characteristics.'); }

    const rankedDifficulties = event.difficulties[event.mode] || [];
    const hardestDifficulty = rankedDifficulties.length
      ? rankedDifficulties[rankedDifficulties.length - 1]._difficulty
      : Object.keys(event.beatmaps[event.mode])[0];
    event.difficulty = this.data.difficulty && event.beatmaps[event.mode][this.data.difficulty]
      ? this.data.difficulty
      : hardestDifficulty;
'''
text = replace_exact(text, old, new, 'default mode and difficulty')
text = text.replace("      if (filename.endsWith('jpg')) {", "      if (filename.toLowerCase().endsWith('jpg') || filename.toLowerCase().endsWith('jpeg')) {", 1)
text = text.replace("      if (filename.endsWith('png')) {", "      if (filename.toLowerCase().endsWith('png')) {", 1)
text = text.replace("      if (filename.endsWith('egg') || filename.endsWith('ogg')) {", "      if (filename.toLowerCase().endsWith('egg') || filename.toLowerCase().endsWith('ogg')) {", 1)
text = text.replace("      event.image = 'assets/img/logo.png';", "      event.image = '';", 1)
text = text.replace("    this.el.emit('challengeloadend', event, false);", "    this.el.emit('challengeloadend', event, false);\n    return event;", 1)
insert_marker = '''  /**
     * From dragged ZIP.
     */
  readFile: function (file) {'''
insert_block = '''  loadArrayBuffer: function (arrayBuffer, options = {}) {
    if (!(arrayBuffer instanceof ArrayBuffer)) {
      return Promise.reject(new Error('Map payload must be an ArrayBuffer.'));
    }
    this.data.id = '';
    this.data.mode = options.mode || this.data.mode || 'Standard';
    this.data.difficulty = options.difficulty || this.data.difficulty || '';
    this.el.emit('challengeloadstart', '', false);

    const blob = new Blob([arrayBuffer], {type: 'application/zip'});
    return ZipLoader.unzip(blob).then(loader => this.processFiles(loader, true)).catch(error => {
      this.isFetching = '';
      this.el.emit('challengeloaderror', null, false);
      throw error;
    });
  },

  /**
     * From dragged ZIP.
     */
  readFile: function (file) {'''
text = replace_exact(text, insert_marker, insert_block, 'in-memory ZIP loader insertion')
text = text.replace("        if (filename.endsWith('info.dat')) {", "        if (filename.toLowerCase().endsWith('info.dat')) {", 1)
write(path, text)

# ---------------------------------------------------------------------------
# Beat generation: selected characteristic, safer arrays and basic 90/360 yaw.
# ---------------------------------------------------------------------------
path = 'src/components/beat-generator.js'
text = read(path)
text = text.replace("    this.rightStageLasers = document.getElementById('rightStageLasers');", "    this.rightStageLasers = document.getElementById('rightStageLasers');\n    this.stage = document.getElementById('stage');\n    this.rotationAngle = 0;", 1)
old = '''    this.el.addEventListener('challengeloadend', evt => {
      this.beatmaps = evt.detail.beatmaps;
      this.beatData = this.beatmaps.Standard[this.data.difficulty || evt.detail.difficulty];
      this.beatSpeeds = evt.detail.beatSpeeds;
      this.info = evt.detail.info;
      this.processBeats();'''
new = '''    this.el.addEventListener('challengeloadend', evt => {
      this.beatmaps = evt.detail.beatmaps;
      const initialMode = evt.detail.mode && this.beatmaps[evt.detail.mode]
        ? evt.detail.mode
        : (this.beatmaps.Standard ? 'Standard' : Object.keys(this.beatmaps)[0]);
      const initialDifficulty = evt.detail.difficulty || this.data.difficulty;
      this.beatData = this.beatmaps[initialMode][initialDifficulty];
      this.beatSpeeds = evt.detail.beatSpeeds;
      this.info = evt.detail.info;
      this.data.mode = initialMode;
      this.data.difficulty = initialDifficulty;
      this.processBeats();'''
text = replace_exact(text, old, new, 'initial characteristic selection')
text = text.replace(
    "      this.beatData = this.beatmaps[this.data.mode][this.data.difficulty];\n      this.processBeats();",
    "      if (!this.beatmaps[this.data.mode] || !this.beatmaps[this.data.mode][this.data.difficulty]) { return; }\n      this.beatData = this.beatmaps[this.data.mode][this.data.difficulty];\n      this.processBeats();",
    1,
)
text = replace_exact(
    text,
    '''    this.beatsTime = 0;
    this.beatsPreloadTime = 0;
    this.beatData._events.sort(lessThan);
    this.beatData._obstacles.sort(lessThan);
    this.beatData._notes.sort(lessThan);
    this.beatSpeed = this.beatSpeeds[this.data.mode][this.data.difficulty];''',
    '''    this.beatsTime = 0;
    this.beatsPreloadTime = 0;
    this.beatData._events = this.beatData._events || [];
    this.beatData._obstacles = this.beatData._obstacles || [];
    this.beatData._notes = this.beatData._notes || [];
    this.beatData._events.sort(lessThan);
    this.beatData._obstacles.sort(lessThan);
    this.beatData._notes.sort(lessThan);
    this.rotationAngle = 0;
    this.applyRotation();
    this.beatSpeed = (this.beatSpeeds[this.data.mode] && this.beatSpeeds[this.data.mode][this.data.difficulty]) || 10;''',
    'safe beat arrays'
)
text = text.replace(
    '''      case 13:
        this.rightStageLasers.components['stage-lasers'].pulse(event._value);
        break;
    }
  },''',
    '''      case 13:
        this.rightStageLasers.components['stage-lasers'].pulse(event._value);
        break;
      case 14:
      case 15:
        this.applyRotationEvent(event._value);
        break;
    }
  },

  applyRotationEvent: function (value) {
    const deltas = {2: -30, 3: -15, 4: 15, 5: 30};
    if (!deltas[value]) { return; }
    this.rotationAngle += deltas[value];
    this.applyRotation();
  },

  applyRotation: function () {
    const radians = THREE.Math.degToRad(-this.rotationAngle);
    if (this.beatContainer) { this.beatContainer.object3D.rotation.y = radians; }
    if (this.stage) { this.stage.object3D.rotation.y = radians; }
  },''',
    1,
)
write(path, text)

# ---------------------------------------------------------------------------
# Controls: build mode/difficulty menus from Info.dat, including 90/360.
# ---------------------------------------------------------------------------
path = 'src/components/song-controls.js'
text = read(path)
text = replace_exact(
    text,
    '''    this.difficultyOptions.addEventListener('click', evt => {
      this.songProgress.innerHTML = formatSeconds(0);
      this.playhead.style.width = '0%';
      this.el.sceneEl.emit('difficultyselect', evt.target.dataset.difficulty, false);
      this.difficulty.innerHTML = evt.target.innerHTML;
      controls.classList.remove('difficultyOptionsActive');
    });''',
    '''    this.difficultyOptions.addEventListener('click', evt => {
      const option = evt.target.closest('[data-difficulty]');
      if (!option) { return; }
      this.songProgress.innerHTML = formatSeconds(0);
      this.playhead.style.width = '0%';
      this.el.sceneEl.emit('difficultyselect', option.dataset.difficulty, false);
      this.difficulty.innerHTML = option.innerHTML;
      controls.classList.remove('difficultyOptionsActive');
    });''',
    'difficulty click handler'
)
text = replace_exact(
    text,
    '''    this.modeOptionEls.addEventListener('click', evt => {
      this.songProgress.innerHTML = formatSeconds(0);
      this.playhead.style.width = '0%';
      this.el.sceneEl.emit('modeselect', evt.target.dataset.mode, false);
      this.modeDropdownEl.innerHTML = evt.target.innerHTML;
      controls.classList.remove('modeOptionsActive');
    });''',
    '''    this.modeOptionEls.addEventListener('click', evt => {
      const option = evt.target.closest('[data-mode]');
      if (!option) { return; }
      this.songProgress.innerHTML = formatSeconds(0);
      this.playhead.style.width = '0%';
      this.el.sceneEl.emit('modeselect', option.dataset.mode, false);
      this.modeDropdownEl.innerHTML = option.innerHTML;
      controls.classList.remove('modeOptionsActive');
    });''',
    'mode click handler'
)
text, count = re.subn(
    r'''  updateModeOptions: function \(\) \{.*?\n  \},\n\n  updateDifficultyOptions: function \(\) \{.*?\n  \},''',
    '''  updateModeOptions: function () {
    this.modeOptionEls.innerHTML = '';
    Object.keys(this.beatmaps).forEach(mode => {
      if (!this.beatmaps[mode] || !Object.keys(this.beatmaps[mode]).length) { return; }
      const option = document.createElement('li');
      option.dataset.mode = mode;
      option.textContent = mode;
      this.modeOptionEls.appendChild(option);
    });
  },

  updateDifficultyOptions: function () {
    const modeDifficulties = this.difficulties[this.data.mode] || [];
    this.difficultyOptions.innerHTML = '';

    modeDifficulties.forEach(difficulty => {
      const option = document.createElement('li');
      option.dataset.difficulty = difficulty._difficulty;
      let label = difficulty._difficulty;
      const customData = difficulty._customData || {};
      if (customData._difficultyLabel) {
        label = customData._difficultyLabel;
        this.customDifficultyLabels[difficulty._difficulty] = label;
      }
      option.textContent = label;
      this.difficultyOptions.appendChild(option);
    });
  },''',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit('Mode/difficulty option functions not found')
write(path, text)

# ---------------------------------------------------------------------------
# High-resolution renderer and parent-window map bridge.
# ---------------------------------------------------------------------------
write('src/components/high-resolution-renderer.js', '''const requestedScale = parseFloat(AFRAME.utils.getUrlParameter('resolution')) || 1.25;

AFRAME.registerComponent('high-resolution-renderer', {
  init: function () {
    this.applyResolution = this.applyResolution.bind(this);
    this.scheduleResolution = this.scheduleResolution.bind(this);
    this.el.addEventListener('renderstart', this.applyResolution);
    window.addEventListener('resize', this.scheduleResolution);
  },

  scheduleResolution: function () {
    requestAnimationFrame(this.applyResolution);
  },

  applyResolution: function () {
    const renderer = this.el.renderer;
    if (!renderer) { return; }
    const deviceRatio = Math.max(1, window.devicePixelRatio || 1);
    const pixelRatio = Math.min(3, Math.max(1, deviceRatio * requestedScale));
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight, false);
  },

  remove: function () {
    this.el.removeEventListener('renderstart', this.applyResolution);
    window.removeEventListener('resize', this.scheduleResolution);
  }
});
''')

write('src/components/simbers-bridge.js', '''const bridgeMode = AFRAME.utils.getUrlParameter('bridge') === '1';

function postToParent (type, extra = {}) {
  if (window.parent === window) { return; }
  window.parent.postMessage(Object.assign({type: type}, extra), '*');
}

AFRAME.registerComponent('simbers-bridge', {
  init: function () {
    if (!bridgeMode) { return; }
    document.body.classList.add('simbersEmbed');
    this.onMessage = this.onMessage.bind(this);
    this.unlockAudio = this.unlockAudio.bind(this);
    window.addEventListener('message', this.onMessage);
    window.addEventListener('pointerdown', this.unlockAudio, {passive: true});
    window.addEventListener('touchstart', this.unlockAudio, {passive: true});
    window.addEventListener('keydown', this.unlockAudio);
  },

  play: function () {
    if (!bridgeMode) { return; }
    this.el.sceneEl.emit('usergesturereceive', null, false);
    setTimeout(() => postToParent('SIMPLIFIED_ARCVIEWER_READY'), 0);
  },

  unlockAudio: function () {
    this.el.sceneEl.emit('usergesturereceive', null, false);
    const analyserEl = document.getElementById('audioAnalyser');
    const analyser = analyserEl && analyserEl.components.audioanalyser;
    if (analyser && analyser.resumeContext) {
      Promise.resolve(analyser.resumeContext()).catch(() => {});
    }
  },

  onMessage: function (event) {
    if (event.source !== window.parent) { return; }
    const data = event.data || {};
    if (data.type !== 'SIMPLIFIED_SABERS_LOAD_MAP') { return; }

    const bytes = data.bytes;
    if (!(bytes instanceof ArrayBuffer) || bytes.byteLength < 32) {
      postToParent('SIMPLIFIED_ARCVIEWER_ERROR', {message: 'Generated map payload is invalid.'});
      return;
    }

    const zipLoader = this.el.components['zip-loader'];
    if (!zipLoader || !zipLoader.loadArrayBuffer) {
      postToParent('SIMPLIFIED_ARCVIEWER_ERROR', {message: 'Map loader is not ready.'});
      return;
    }

    postToParent('SIMPLIFIED_ARCVIEWER_MAP_ACCEPTED');
    zipLoader.loadArrayBuffer(bytes, {
      mode: data.mode || 'Standard',
      difficulty: data.difficulty || 'ExpertPlus'
    }).then(result => {
      this.unlockAudio();
      postToParent('SIMPLIFIED_ARCVIEWER_STARTED', {
        modes: Object.keys(result.beatmaps || {}),
        mode: result.mode,
        difficulty: result.difficulty
      });
    }).catch(error => {
      console.error(error);
      postToParent('SIMPLIFIED_ARCVIEWER_ERROR', {
        message: error && error.message ? error.message : String(error)
      });
    });
  },

  remove: function () {
    if (!bridgeMode) { return; }
    window.removeEventListener('message', this.onMessage);
    window.removeEventListener('pointerdown', this.unlockAudio);
    window.removeEventListener('touchstart', this.unlockAudio);
    window.removeEventListener('keydown', this.unlockAudio);
  }
});
''')

# ---------------------------------------------------------------------------
# Compact embedded controls and mobile-safe viewer layout.
# ---------------------------------------------------------------------------
path = 'src/index.styl'
text = read(path)
text += '''\n\n/* Simplified Sabers embedded viewer */\nbody.simbersEmbed\n  margin 0\n  overflow hidden\n\n  #search,\n  #subscribeForm,\n  .github-corner\n    display none !important\n\n  #controls\n    background rgba(5, 5, 8, 0.88)\n    border 1px solid rgba(255,255,255,0.12)\n    border-radius 6px\n    box-sizing border-box\n    margin-bottom 8px\n    max-width calc(100vw - 16px)\n    padding 8px\n    width 760px\n\n  #songInfoContainer\n    min-width 0\n\n  #songInfo\n    max-width 160px\n    overflow hidden\n\n@media (max-width: 720px)\n  body.simbersEmbed\n    #controls\n      flex-wrap wrap\n      gap 6px\n      justify-content center\n      width calc(100vw - 12px)\n\n    #timeline\n      flex 1 1 120px\n      min-width 90px\n\n    #songInfoContainer\n      flex 1 1 100%\n      padding-top 2px\n\n    #songInfoSelect\n      position static\n      margin-left auto\n\n    #songTime\n      margin-left 4px\n      width 62px\n'''
write(path, text)

# Basic static assertions.
assert 'CLICK ANYWHERE TO PLAY' not in read('src/templates/loading.html')
assert 'id="logo"' not in read('src/templates/stage.html')
assert 'SIMPLIFIED_SABERS_LOAD_MAP' in read('src/components/simbers-bridge.js')
assert '90Degree' in read('src/templates/controls.html')
print('Patched browser-native viewer for Simplified Sabers integration')

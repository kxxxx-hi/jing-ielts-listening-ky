# app.py
import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="English Listening Helper", layout="wide")

# ------- Load external data.json safely -------
DATA_PATH = Path("data.json")
if DATA_PATH.exists():
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {}
else:
    data = {}

# ------- Build payload strictly from data.json keys (with fallbacks) -------
payload = {
    "flashcardList": (
        data.get("flashcardList")
        or data.get("flashcards")
        or ["eloquent","gregarious","resilience","ubiquitous","ephemeral",
            "serendipity","magnanimous","perspicacious","conundrum","juxtaposition"]
    ),
    "antonymData": data.get("antonymData") or data.get("antonym") or [],
    "pronunciationData": data.get("pronunciationData") or data.get("pronunciation") or [],
    "minimalPairsData": data.get("minimalPairsData") or data.get("minimalPairs") or [],
    "vocabData": data.get("vocabData") or [],
    "tongueTwisterData": (
        data.get("tongueTwisterData")
        or data.get("tongueTwisters")
        or data.get("tongue_twisters")
        or []
    ),
}

# ------- HTML (JS app) -------
html_template = r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0" />
<title>English Listening Helper</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  body { font-family: 'Inter', sans-serif; }
  .tab-active { border-color:#4f46e5; color:#4f46e5; background-color:#eef2ff; }
  .card { min-height:20rem; display:flex; flex-direction:column; justify-content:center; align-items:center; }
  .btn-choice { transition: all .2s ease-in-out; }
  .btn-choice:hover { transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgb(0 0 0 / .1), 0 2px 4px -2px rgb(0 0 0 / .1); }
  .correct { background-color:#10b981 !important; color:#fff !important; border-color:#059669 !important; }
  .incorrect { background-color:#ef4444 !important; color:#fff !important; border-color:#dc2626 !important; }
  .ph-blue { color:#2563eb; font-weight:600; }
  .ph-red { color:#dc2626; font-weight:600; }
  .ph-yellow { color:#b45309; font-weight:600; }
  .tw-sentence { font-size:1.2rem; line-height:1.75rem; text-align:center; }
  .ph-chip { padding:2px 6px; border-radius:8px; background:#eef2ff; margin:0 4px; }
</style>
</head>
<body class="bg-gray-100 text-gray-800 flex items-center justify-center min-h-screen p-4">

<div class="w-full max-w-2xl mx-auto bg-white rounded-2xl shadow-lg p-6 md:p-8">
  <header class="text-center mb-6">
    <h1 class="text-3xl font-bold text-gray-900">English Listening Helper</h1>
    <p class="text-gray-500 mt-1">Practice your vocabulary and listening skills.</p>
  </header>

  <!-- Tabs -->
  <div class="border-b border-gray-200 mb-6">
    <nav class="-mb-px flex flex-wrap gap-2" aria-label="Tabs">
      <button id="tab-flashcards" class="whitespace-nowrap py-3 px-2 border-b-2 font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300">Flashcards</button>
      <button id="tab-antonym" class="whitespace-nowrap py-3 px-2 border-b-2 font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300">Antonym Game</button>
      <button id="tab-pronunciation" class="whitespace-nowrap py-3 px-2 border-b-2 font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300">Pronunciation Game</button>
      <button id="tab-minimalpairs" class="whitespace-nowrap py-3 px-2 border-b-2 font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300">Which one are you hearing?</button>
      <button id="tab-tonguetwister" class="whitespace-nowrap py-3 px-2 border-b-2 font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300">Tongue Twister</button>
    </nav>
  </div>

  <main>
    <!-- Flashcards -->
    <div id="view-flashcards" class="space-y-6">
      <div>
        <label for="correct-list" class="block text-sm font-medium text-gray-700">Customize word list (comma-separated)</label>
        <textarea id="correct-list" rows="3" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" placeholder="e.g., apple, beautiful, challenge"></textarea>
        <button id="save-list-btn" class="mt-2 w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none">Save and Use This List</button>
      </div>

      <div class="bg-gray-50 rounded-lg p-6 text-center shadow-inner">
        <div id="flashcard-container" class="card">
          <p id="flashcard-instruction" class="text-gray-500 mb-4">Click the speaker to hear the word.</p>
          <button id="play-audio-btn" class="w-24 h-24 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 hover:bg-indigo-200 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
          </button>
          <div id="correct-reveal" class="mt-4 h-10">
            <h2 id="correct-text" class="text-4xl font-bold text-gray-800 invisible"></h2>
          </div>
        </div>
        <button id="reveal-correct-btn" class="mt-4 inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50">Reveal word</button>
      </div>

      <div class="flex justify-between items-center">
        <button id="prev-correct-btn" class="p-3 rounded-full bg-gray-200 hover:bg-gray-300">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </button>
        <span id="correct-counter" class="text-sm font-medium text-gray-600">1 / 10</span>
        <button id="next-correct-btn" class="p-3 rounded-full bg-gray-200 hover:bg-gray-300">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </button>
      </div>
    </div>

    <!-- Antonym -->
    <div id="view-antonym" class="hidden space-y-6">
      <div class="bg-gray-50 rounded-lg p-6 text-center shadow-inner card">
        <h3 class="text-xl font-semibold text-gray-800 mb-2">Exclude the antonym</h3>
        <p class="text-gray-500 mb-6">Three are synonyms. Click the antonym.</p>
        <div id="antonym-choices" class="grid grid-cols-2 gap-4 w-full max-w-md"></div>
      </div>
      <div id="antonym-feedback" class="h-6 text-center font-medium"></div>
    </div>

    <!-- Pronunciation (4-choice) -->
    <div id="view-pronunciation" class="hidden space-y-6">
      <div class="bg-gray-50 rounded-lg p-6 text-center shadow-inner card">
        <h3 class="text-xl font-semibold text-gray-800 mb-2">Choose the word you hear</h3>
        <p class="text-gray-500 mb-6">Listen and click the match.</p>
        <button id="play-pronunciation-audio-btn" class="mb-6 w-24 h-24 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 hover:bg-indigo-200 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
        </button>
        <div id="pronunciation-choices" class="grid grid-cols-2 gap-4 w-full max-w-md"></div>
      </div>
      <div id="pronunciation-feedback" class="h-6 text-center font-medium"></div>
    </div>

    <!-- Minimal Pairs (2-choice) -->
    <div id="view-minimalpairs" class="hidden space-y-6">
      <div class="bg-gray-50 rounded-lg p-6 text-center shadow-inner card">
        <h3 class="text-xl font-semibold text-gray-800 mb-2">Which one are you hearing?</h3>
        <p class="text-gray-500 mb-6">Click the speaker, then choose.</p>
        <button id="play-minimalpairs-audio-btn" class="mb-6 w-24 h-24 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 hover:bg-indigo-200 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
        </button>
        <div id="minimalpairs-choices" class="grid grid-cols-2 gap-4 w-full max-w-md"></div>
      </div>
      <div id="minimalpairs-feedback" class="h-6 text-center font-medium"></div>
    </div>

    <!-- Tongue Twister (flashcards) -->
    <div id="view-tonguetwister" class="hidden space-y-6">
      <div class="bg-gray-50 rounded-lg p-6 shadow-inner">
        <div class="flex flex-col items-center gap-2 mb-3">
          <div id="tw-group" class="text-sm font-semibold text-indigo-700"></div>
          <div id="tw-phonemes" class="text-sm"></div>
        </div>
        <div class="card px-4 py-6">
          <p id="tw-sentence" class="tw-sentence"></p>
          <div class="mt-6 flex gap-3">
            <button id="tw-play-normal" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md bg-white text-gray-700 hover:bg-gray-50">
              ▶ Play
            </button>
            <button id="tw-play-slow" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md bg-white text-gray-700 hover:bg-gray-50">
              ▶ Slow
            </button>
          </div>
        </div>
        <div class="flex justify-between items-center mt-4">
          <button id="tw-prev" class="p-3 rounded-full bg-gray-200 hover:bg-gray-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <span id="tw-counter" class="text-sm font-medium text-gray-600">1 / 1</span>
          <button id="tw-next" class="p-3 rounded-full bg-gray-200 hover:bg-gray-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      </div>
    </div>

  </main>
</div>

<script>
  // Data injected by Python
  window.APP_DATA = __DATA_JSON__;
  const safeArray = (v) => Array.isArray(v) ? v : [];

  document.addEventListener('DOMContentLoaded', () => {
    // --- STATE ---
    let currentMode = 'flashcards';
    let correctList = safeArray(window.APP_DATA.flashcardList).slice(0);
    let currentcorrectIndex = 0;
    const synth = window.speechSynthesis;

    const antonymData = safeArray(window.APP_DATA.antonymData);
    const pronunciationData = safeArray(window.APP_DATA.pronunciationData);
    const minimalPairsData = safeArray(window.APP_DATA.minimalPairsData);
    const tongueTwisterData = safeArray(window.APP_DATA.tongueTwisterData);

    // Build deck
    const twDeck = [];
    tongueTwisterData.forEach(g => {
      (g.sentences || []).forEach(s => {
        const htmlMarked = ('' + s)
          .replace(/\[\[1\]\]([\s\S]*?)\[\[\/\]\]/g, '<span class="ph-blue">$1</span>')
          .replace(/\[\[2\]\]([\s\S]*?)\[\[\/\]\]/g, '<span class="ph-red">$1</span>')
          .replace(/\[\[3\]\]([\s\S]*?)\[\[\/\]\]/g, '<span class="ph-yellow">$1</span>');
        twDeck.push({ group: g.group, phonemes: g.phonemes || [], patterns: g.patterns || null, sentence: s, htmlMarked });
      });
    });
    let twIndex = 0;

    // --- DOM ELEMENTS ---
    const views = {
      flashcards: document.getElementById('view-flashcards'),
      antonym: document.getElementById('view-antonym'),
      pronunciation: document.getElementById('view-pronunciation'),
      minimalpairs: document.getElementById('view-minimalpairs'),
      tonguetwister: document.getElementById('view-tonguetwister'),
    };
    const tabs = {
      flashcards: document.getElementById('tab-flashcards'),
      antonym: document.getElementById('tab-antonym'),
      pronunciation: document.getElementById('tab-pronunciation'),
      minimalpairs: document.getElementById('tab-minimalpairs'),
      tonguetwister: document.getElementById('tab-tonguetwister'),
    };

    // Flashcard Elements
    const correctListInput = document.getElementById('correct-list');
    const saveListBtn = document.getElementById('save-list-btn');
    const playAudioBtn = document.getElementById('play-audio-btn');
    const revealcorrectBtn = document.getElementById('reveal-correct-btn');
    const correctText = document.getElementById('correct-text');
    const prevcorrectBtn = document.getElementById('prev-correct-btn');
    const nextcorrectBtn = document.getElementById('next-correct-btn');
    const correctCounter = document.getElementById('correct-counter');
    const flashcardInstruction = document.getElementById('flashcard-instruction');

    // Antonym
    const antonymChoicesContainer = document.getElementById('antonym-choices');
    const antonymFeedback = document.getElementById('antonym-feedback');
    let currentAntonymQuestion = null;

    // Pronunciation
    const playPronunciationAudioBtn = document.getElementById('play-pronunciation-audio-btn');
    const pronunciationChoicesContainer = document.getElementById('pronunciation-choices');
    const pronunciationFeedback = document.getElementById('pronunciation-feedback');
    let currentPronunciationQuestion = null;

    // Minimal Pairs
    const playMinimalPairsAudioBtn = document.getElementById('play-minimalpairs-audio-btn');
    const minimalPairsChoicesContainer = document.getElementById('minimalpairs-choices');
    const minimalPairsFeedback = document.getElementById('minimalpairs-feedback');
    let currentMinimalPairsQuestion = null;

    // Tongue Twister
    const twGroupEl = document.getElementById('tw-group');
    const twPhonemesEl = document.getElementById('tw-phonemes');
    const twSentenceEl = document.getElementById('tw-sentence');
    const twPrevBtn = document.getElementById('tw-prev');
    const twNextBtn = document.getElementById('tw-next');
    const twCounter = document.getElementById('tw-counter');
    const twPlayNormal = document.getElementById('tw-play-normal');
    const twPlaySlow = document.getElementById('tw-play-slow');

    // --- Utils ---
    const speak = (text, rate=0.9) => {
      if (!text) return;
      if (synth.speaking) synth.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'en-US';
      u.rate = rate;
      synth.speak(u);
    };
    const shuffleArray = (array) => {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    };
    const renderPhonemeLegend = (phonemes) => {
      const classes = ['ph-blue','ph-red','ph-yellow'];
      return phonemes.slice(0,3).map((p, i) => `<span class="ph-chip ${classes[i]}">${p}</span>`).join('');
    };

    function highlightWithPatterns(text, patternsByIdx) {
      if (!patternsByIdx || !patternsByIdx.length) return text;
      const classes = ['ph-blue','ph-red','ph-yellow'];
      const matches = [];
      patternsByIdx.slice(0,3).forEach((arr, idx) => {
        (arr || []).forEach(pat => {
          try {
            const re = new RegExp(pat, 'gi');
            let m;
            while ((m = re.exec(text)) !== null) {
              matches.push({ start: m.index, end: m.index + m[0].length, idx, str: m[0] });
              if (re.lastIndex === m.index) re.lastIndex++;
            }
          } catch(e) { }
        });
      });
      matches.sort((a,b)=> a.start - b.start || (b.end - b.start) - (a.end - a.start));
      const picked = [];
      let lastEnd = -1;
      for (const m of matches) {
        if (m.start >= lastEnd) { picked.push(m); lastEnd = m.end; }
      }
      if (!picked.length) return text;
      let out = '';
      let cursor = 0;
      picked.forEach(m => {
        out += text.slice(cursor, m.start);
        out += `<span class="${classes[m.idx]}">` + text.slice(m.start, m.end) + '</span>';
        cursor = m.end;
      });
      out += text.slice(cursor);
      return out;
    }

    const switchMode = (mode) => {
      Object.values(views).forEach(v => v.classList.add('hidden'));
      Object.values(tabs).forEach(t => t.classList.remove('tab-active'));
      views[mode].classList.remove('hidden');
      tabs[mode].classList.add('tab-active');
      if (mode === 'antonym') setupAntonymGame();
      if (mode === 'pronunciation') setupPronunciationGame();
      if (mode === 'minimalpairs') setupMinimalPairsGame();
      if (mode === 'tonguetwister') updateTwView();
    };

    // --- Flashcards ---
    const updateFlashcardView = () => {
      const word = correctList[currentcorrectIndex] || '';
      flashcardInstruction.classList.remove('hidden');
      correctText.textContent = word;
      correctText.classList.add('invisible');
      correctCounter.textContent = `${correctList.length ? currentcorrectIndex + 1 : 0} / ${correctList.length}`;
    };
    const savecorrectList = () => {
      const words = (correctListInput.value || '')
        .split(',').map(s => s.trim()).filter(Boolean);
      if (words.length) {
        correctList = words;
        currentcorrectIndex = 0;
        updateFlashcardView();
      }
    };

    // Flashcards wiring (fix for no response to click)
    saveListBtn.addEventListener('click', savecorrectList);
    playAudioBtn.addEventListener('click', () => {
      if (!correctList.length) return;
      speak(correctList[currentcorrectIndex], 0.95);
    });
    revealcorrectBtn.addEventListener('click', () => {
      correctText.classList.remove('invisible');
      flashcardInstruction.classList.add('hidden');
    });
    prevcorrectBtn.addEventListener('click', () => {
      if (!correctList.length) return;
      currentcorrectIndex = (currentcorrectIndex - 1 + correctList.length) % correctList.length;
      updateFlashcardView();
    });
    nextcorrectBtn.addEventListener('click', () => {
      if (!correctList.length) return;
      currentcorrectIndex = (currentcorrectIndex + 1) % correctList.length;
      updateFlashcardView();
    });

    // --- Antonym Game ---
    const setupAntonymGame = () => {
      if (!antonymData.length) {
        antonymChoicesContainer.innerHTML = '<p class="text-gray-500">No antonym data.</p>';
        antonymFeedback.textContent = '';
        return;
      }
      antonymFeedback.textContent = '';
      const q = antonymData[Math.floor(Math.random() * antonymData.length)];
      const choices = shuffleArray([...(q.s || []), q.a]);
      antonymChoicesContainer.innerHTML = '';
      choices.forEach(choice => {
        const b = document.createElement('button');
        b.textContent = choice;
        b.className = 'btn-choice w-full px-4 py-3 border border-gray-300 rounded-lg text-lg font-medium bg-white text-gray-700 hover:bg-gray-50';
        b.onclick = () => {
          const buttons = antonymChoicesContainer.querySelectorAll('button');
          buttons.forEach(btn => {
            btn.disabled = true;
            if (btn.textContent === q.a) btn.classList.add('correct');
            else if (btn.textContent === choice) btn.classList.add('incorrect');
          });
          antonymFeedback.textContent = (choice === q.a) ? 'Correct!' : 'Not quite. Try the next one!';
          antonymFeedback.className = 'h-6 text-center font-medium ' + ((choice === q.a) ? 'text-green-600' : 'text-red-600');
          setTimeout(setupAntonymGame, 1600);
        };
        antonymChoicesContainer.appendChild(b);
      });
    };

    // --- Pronunciation Game (4 options) ---
    const setupPronunciationGame = () => {
      if (!pronunciationData.length) {
        pronunciationChoicesContainer.innerHTML = '<p class="text-gray-500">No pronunciation data.</p>';
        pronunciationFeedback.textContent = '';
        currentPronunciationQuestion = null;
        return;
      }
      pronunciationFeedback.textContent = '';
      currentPronunciationQuestion = pronunciationData[Math.floor(Math.random() * pronunciationData.length)];
      const allChoices = [currentPronunciationQuestion.correct, ...(currentPronunciationQuestion.distractors || [])];
      const choices = shuffleArray(allChoices).slice(0,4);
      pronunciationChoicesContainer.innerHTML = '';
      choices.forEach(choice => {
        const b = document.createElement('button');
        b.textContent = choice;
        b.className = 'btn-choice w-full px-4 py-3 border border-gray-300 rounded-lg text-lg font-medium bg-white text-gray-700 hover:bg-gray-50';
        b.onclick = () => {
          const buttons = pronunciationChoicesContainer.querySelectorAll('button');
          buttons.forEach(btn => {
            btn.disabled = true;
            if (btn.textContent === currentPronunciationQuestion.correct) btn.classList.add('correct');
            else if (btn.textContent === choice) btn.classList.add('incorrect');
          });
          const ok = (choice === currentPronunciationQuestion.correct);
          pronunciationFeedback.textContent = ok ? 'Correct!' : 'Not quite. Try the next one!';
          pronunciationFeedback.className = 'h-6 text-center font-medium ' + (ok ? 'text-green-600' : 'text-red-600');
          setTimeout(setupPronunciationGame, 1600);
        };
        pronunciationChoicesContainer.appendChild(b);
      });
    };

    playPronunciationAudioBtn.addEventListener('click', () => {
      const phrase = currentPronunciationQuestion && currentPronunciationQuestion.correct
        ? currentPronunciationQuestion.correct
        : (pronunciationData[0] ? pronunciationData[0].correct : '');
      speak(phrase, 0.9);
    });

    // --- Minimal Pairs (2 options) ---
    const setupMinimalPairsGame = () => {
      if (!minimalPairsData.length) {
        minimalPairsChoicesContainer.innerHTML = '<p class="text-gray-500">No minimal-pairs data.</p>';
        minimalPairsFeedback.textContent = '';
        currentMinimalPairsQuestion = null;
        return;
      }
      minimalPairsFeedback.textContent = '';
      const q = minimalPairsData[Math.floor(Math.random() * minimalPairsData.length)];
      const target = Math.random() < 0.5 ? q.correct : q.distractor;
      currentMinimalPairsQuestion = { ...q, target };
      const choices = shuffleArray([q.correct, q.distractor]);
      minimalPairsChoicesContainer.innerHTML = '';
      choices.forEach(choice => {
        const b = document.createElement('button');
        b.textContent = choice;
        b.className = 'btn-choice w-full px-4 py-3 border border-gray-300 rounded-lg text-lg font-medium bg-white text-gray-700 hover:bg-gray-50';
        b.onclick = () => {
          const buttons = minimalPairsChoicesContainer.querySelectorAll('button');
          buttons.forEach(btn => {
            btn.disabled = true;
            if (btn.textContent === currentMinimalPairsQuestion.target) btn.classList.add('correct');
            else if (btn.textContent === choice) btn.classList.add('incorrect');
          });
          const ok = (choice === currentMinimalPairsQuestion.target);
          minimalPairsFeedback.textContent = ok ? 'Correct!' : 'Not quite. Try the next one!';
          minimalPairsFeedback.className = 'h-6 text-center font-medium ' + (ok ? 'text-green-600' : 'text-red-600');
          setTimeout(setupMinimalPairsGame, 1600);
        };
        minimalPairsChoicesContainer.appendChild(b);
      });
    };

    playMinimalPairsAudioBtn.addEventListener('click', () => {
      const phrase = currentMinimalPairsQuestion && currentMinimalPairsQuestion.target
        ? currentMinimalPairsQuestion.target
        : (minimalPairsData[0] ? minimalPairsData[0].correct : '');
      speak(phrase, 0.9);
    });

    // --- Tongue Twister (flashcards) ---
    function computeHighlightedSentence(item) {
      const hadInline = item.htmlMarked && item.htmlMarked !== item.sentence;
      if (hadInline) return item.htmlMarked;
      if (item.patterns && item.patterns.length) {
        return highlightWithPatterns(item.sentence, item.patterns);
      }
      return item.sentence;
    }

    const updateTwView = () => {
      if (!twDeck.length) {
        twGroupEl.textContent = '';
        twPhonemesEl.innerHTML = '<span class="text-gray-500">No tongue twisters.</span>';
        twSentenceEl.textContent = '';
        twCounter.textContent = '0 / 0';
        return;
      }
      const item = twDeck[twIndex];
      twGroupEl.textContent = item.group || '';
      twPhonemesEl.innerHTML = renderPhonemeLegend(item.phonemes || []);
      twSentenceEl.innerHTML = computeHighlightedSentence(item);
      twCounter.textContent = `${twIndex + 1} / ${twDeck.length}`;
    };

    twPrevBtn.addEventListener('click', () => { if (!twDeck.length) return; twIndex = (twIndex - 1 + twDeck.length) % twDeck.length; updateTwView(); });
    twNextBtn.addEventListener('click', () => { if (!twDeck.length) return; twIndex = (twIndex + 1) % twDeck.length; updateTwView(); });
    twPlayNormal.addEventListener('click', () => { if (!twDeck.length) return; speak(twDeck[twIndex].sentence, 1.0); });
    twPlaySlow.addEventListener('click', () => { if (!twDeck.length) return; speak(twDeck[twIndex].sentence, 0.7); });

    // --- Tab wiring ---
    Object.keys(tabs).forEach(key => tabs[key].addEventListener('click', () => switchMode(key)));

    // --- Init ---
    document.getElementById('correct-list').value = correctList.join(', ');
    updateFlashcardView();
    switchMode('flashcards');
  });
</script>
</body>
</html>
'''

# Inject JSON safely without f-strings
html_content = html_template.replace(
    "__DATA_JSON__",
    json.dumps(payload, ensure_ascii=False)
)

components.html(html_content, height=900, scrolling=True)

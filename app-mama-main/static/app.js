// Liste des verbes irréguliers (base, prétérit, participe passé)
const verbs = [
  { base: "be", past: "was/were", pp: "been" },
  { base: "have", past: "had", pp: "had" },
  { base: "do", past: "did", pp: "done" },
  { base: "say", past: "said", pp: "said" },
  { base: "sling", past: "slung", pp: "slung" }  // exemple inclus
];

let currentVerb = null;
let score = 0;
let attempts = 0;

// Choisir un nouveau verbe au hasard
function pickNewVerb() {
  const randomIndex = Math.floor(Math.random() * verbs.length);
  currentVerb = verbs[randomIndex];
  document.getElementById('base-verb').textContent = currentVerb.base;
  // Réinitialiser les champs et le message pour la nouvelle question
  document.getElementById('past').value = "";
  document.getElementById('participle').value = "";
  document.getElementById('feedback').textContent = "";
  document.getElementById('feedback').className = 'feedback';
}

// Mettre à jour la barre de progression et le texte
function updateProgress() {
  const percent = attempts > 0 ? Math.round((score / attempts) * 100) : 0;
  document.getElementById('progress-text').textContent = 
    `${score} / ${attempts} (${percent}%)`;
  document.getElementById('progress-bar').style.width = percent + "%";
}

// Événement du bouton Valider (vérifier la réponse)
document.getElementById('validateBtn').addEventListener('click', () => {
  if (!currentVerb) return;
  const pastInput = document.getElementById('past').value.trim();
  const ppInput = document.getElementById('participle').value.trim();
  // Vérifier que les deux champs sont remplis
  if (!pastInput || !ppInput) {
    document.getElementById('feedback').textContent = 
      "Veuillez remplir les deux champs.";
    document.getElementById('feedback').className = 'feedback incorrect';
    return;
  }
  // Mettre à jour le nombre de tentatives
  attempts++;
  // Vérifier la réponse (insensible à la casse)
  const isCorrect = pastInput.toLowerCase() === currentVerb.past.toLowerCase() &&
                    ppInput.toLowerCase() === currentVerb.pp.toLowerCase();
  if (isCorrect) {
    score++;
    document.getElementById('feedback').textContent = "Correct ! ✔";
    document.getElementById('feedback').className = 'feedback correct';
  } else {
    document.getElementById('feedback').textContent = "Incorrect... Les réponses étaient : " +
      `${currentVerb.past} / ${currentVerb.pp}`;
    document.getElementById('feedback').className = 'feedback incorrect';
  }
  updateProgress();
});

// Événement du bouton Nouveau (passer à une nouvelle question)
document.getElementById('newBtn').addEventListener('click', () => {
  pickNewVerb();
});

// Événement du bouton Reset (réinitialiser le quiz)
document.getElementById('resetBtn').addEventListener('click', () => {
  score = 0;
  attempts = 0;
  updateProgress();
  pickNewVerb();
});

// Initialiser le premier verbe au chargement de la page
window.addEventListener('load', () => {
  pickNewVerb();
});
const API_BASE = "https://verbsquiz.onrender.com";   // ← ou l’URL ngrok

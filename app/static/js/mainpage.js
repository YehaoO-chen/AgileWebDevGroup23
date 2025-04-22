/* JS for Timer function */

let focusTime = 50;
let breakTime = 10;
let remainingSeconds = 0;
let isFocus = true;
let isPaused = false;
let timer = null;

function setTimeValue(type, value) {
  // Restricting the minimum and maximum input value (if the input value is less than 1, then change to 1; if is more than 180, then change to 1)
  // Ensure the input does not exceed the scope
  value = Math.max(1, Math.min(180, value));
  // Match the selected type of time (Focus or Break) with its id
  const input = document.getElementById(`${type}-time`);
  input.value = value;

  if (type === 'focus') {
    focusTime = value;
  } else {
    breakTime = value;
  }
}

// Function for the "+" & "-" adjust buttons
function adjustTime(type, delta) {
  const currentValue = type === 'focus' ? focusTime : breakTime;
  setTimeValue(type, currentValue + delta);
}

// Function for the users to mannually adjust the time 
function sanitizeInput(input, type) {
  // Restrict the maximum length of input (3 digits) and screen out all the non-digit input
  input.value = input.value.replace(/[^\d]/g, '').slice(0, 3); 

  // Because 'getElementById' method always returns string, therefore, use ParseInt() to change it into integer
  let value = parseInt(input.value, 10);
  if (isNaN(value)) return;

  setTimeValue(type, value);
}

// Copilot generated - ensure whenever the user types, it gets cleaned and limited 3 digits
window.addEventListener('DOMContentLoaded', () => {
  ['focus', 'break'].forEach(type => {
    const input = document.getElementById(`${type}-time`);
    input.addEventListener('input', () => sanitizeInput(input, type));
  });
});

// update the input value
function updateTimeFromInput(type) {
  const input = document.getElementById(`${type}-time`);
  sanitizeInput(input, type); 
}

function startTimer() {
  updateTimeFromInput('focus');
  updateTimeFromInput('break');

  document.getElementById('setup-area').style.display = 'none';
  document.getElementById('floating-timer').classList.add('show');
 

  if (timer) return;
  
  if (remainingSeconds === 0) {
    remainingSeconds = (isFocus ? focusTime : breakTime) * 60;
  }
  updateCountdownDisplay();
  timer = setInterval(() => {
    if (!isPaused) {
      remainingSeconds--;
      updateCountdownDisplay();

      if (remainingSeconds <= 0) {
        clearInterval(timer);
        timer = null;
        showPopup();
        
      }
    }
  }, 1000);
}

function pauseTimer() {
    isPaused = !isPaused;

    const pausePath = document.getElementById('pause-path');
    
    if (isPaused) {
        pausePath.setAttribute("d", "M22 11v2h-1v1h-1v1h-2v1h-2v1h-1v1h-2v1h-2v1h-1v1H8v1H6v1H3v-1H2V2h1V1h3v1h2v1h2v1h1v1h2v1h2v1h1v1h2v1h2v1h1v1z");
      } else {
        pausePath.setAttribute("d", "M23 2v20h-1v1h-7v-1h-1V2h1V1h7v1zM9 2h1v20H9v1H2v-1H1V2h1V1h7z");
      }
}

function resetTimer() {
  clearInterval(timer);
  timer = null;
  isPaused = false;
  remainingSeconds = 0;
  isFocus = true;
  updateCountdownDisplay();

  document.getElementById('floating-timer').classList.remove('show');
  document.getElementById('setup-area').style.display = 'block';
}

function updateCountdownDisplay() {
  const min = Math.floor(remainingSeconds / 60).toString().padStart(2, '0');
  const sec = (remainingSeconds % 60).toString().padStart(2, '0');
  // Match different type of mode to better differentiate what the current timer is for
  const emoji = isFocus ? "✍🏻" : "☕";
  const emoji2 = isFocus ? "📖" : "🍫"

  document.getElementById("countdown-display").textContent = `${emoji} ${min}:${sec} ${emoji2}`;
}

function backToSetup() {
  resetTimer();
}

function showPopup() {
  const times = isFocus ? focusTime : breakTime;
  const formatted = `${String(times).padStart(2, '0')}:00`; 

  document.getElementById("completed_time").textContent= formatted;
  document.getElementById("popup-window").style.display= 'block';
  document.getElementById('floating-timer').classList.remove('show');

}

function closePopup() {
  document.getElementById("popup-window").style.display='none';
  document.getElementById('setup-area').style.display = 'block';
}

function takeBreak() {
  document.getElementById("popup-window").style.display='none';
  document.getElementById('floating-timer').classList.add('show');


  isFocus = false;
  isPaused = false;
  remainingSeconds = breakTime * 60;
  updateCountdownDisplay();
  if (timer) clearInterval(timer);
  
  timer = setInterval(() => {
    if (!isPaused) {

      remainingSeconds--;
      updateCountdownDisplay();

      if (remainingSeconds <= 0) {
        clearInterval(timer);
        timer = null;
        document.getElementById("floating-timer").classList.remove("show");
        document.getElementById("break-window").style.display='block';
        
      }
    }
  }, 1000);
}

function ContinueFocus() {
  startTimer();
  document.getElementById("break-window").style.display='none';
}

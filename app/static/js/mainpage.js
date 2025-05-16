/* Timer widget JS */
// Initialise the default value

window.focusTime = window.focusTime || 50; 
window.breakTime = window.breakTime || 10; 
window.remainingSeconds = window.remainingSeconds || 0; 
window.isFocus = window.isFocus ?? true; 
window.isPaused = window.isPaused ?? false; 
window.timer = window.timer || null; 


function saveTimerState() {
  localStorage.setItem('remainingSeconds', window.remainingSeconds);
  localStorage.setItem('isFocus', window.isFocus);
  localStorage.setItem('timerRunning', window.timer ? 'true' : 'false');
}


function restoreTimerState() {
  const storedRemaining = parseInt(localStorage.getItem('remainingSeconds'), 10);
  const storedIsFocus = localStorage.getItem('isFocus') === 'true';
  const storedRunning = localStorage.getItem('timerRunning') === 'true';

  if (storedRunning && storedRemaining > 0) {
    window.remainingSeconds = storedRemaining;
    window.isFocus = storedIsFocus;
    window.isPaused = false;
    updateCountdownDisplay();
    document.getElementById('setup-area').style.display = 'none';
    document.getElementById('floating-timer').classList.add('show');

    window.timer = setInterval(() => {
      if (!window.isPaused) {
        window.remainingSeconds--;
        updateCountdownDisplay();
        saveTimerState();
        if (window.remainingSeconds <= 0) {
          clearInterval(window.timer);
          window.timer = null;
          showPopup();
          localStorage.setItem('timerRunning', 'false');
        }
      }
    }, 1000);
  }
}


function restoreBackgroundAndMusic() {
  const savedBg = localStorage.getItem('bgSelected');
  if (savedBg) {
    bgDiv.style.backgroundImage = `url('/static/gifs/${savedBg}')`;
    bgSelect.value = savedBg;
  }

  const savedMusic = localStorage.getItem('musicSelected');
  if (savedMusic) {
    audio.src = `/static/audio/${savedMusic}`;
    musicSelect.value = savedMusic;
  }

  const savedVolume = parseFloat(localStorage.getItem('volume'));
  if (!isNaN(savedVolume)) {
    audio.volume = savedVolume;
    volumeSlider.value = savedVolume;
  }

  const savedMuted = localStorage.getItem('muted') === 'true';
  audio.muted = savedMuted;
  toggleMuteBtn.textContent = savedMuted ? 'Unmute' : 'Mute';
} 

window.pauseCount = 0;
window.currentSessionStartTime = null;
window.currentSessionInitialFocusTime = 0; // To store focusTime at the start of a session

    // Ensure time is within allowed range (1-180)
  // Ensure the input does not exceed the scope
  function setTimeValue(type, value) {
    value = Math.max(1, Math.min(180, value));
      // Match the selected type of time (Focus or Break) with its id
    const input = document.getElementById(`${type}-time`);
    input.value = value;
    if (type === 'focus') focusTime = value;
    else breakTime = value;
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
    // Convert input to integer after removing non-digit characters
    let value = parseInt(input.value, 10);
    if (isNaN(value)) return;
    setTimeValue(type, value);
  }
  
  
  window.setupArea = document.getElementById('setup-area');
  if (window.setupArea) {
    window.setupArea.classList.add('animate');
    window.setupArea.addEventListener('animationend', () => window.setupArea.classList.remove('animate'));
  }

  window.todoContainer = document.querySelector('.todo-container');
  if (window.todoContainer) {
    window.todoContainer.classList.add('animate');
    window.todoContainer.addEventListener('animationend', () => window.todoContainer.classList.remove('animate'));
  }

  window.background = document.getElementById('audio-widget');
  if (window.background) {
    window.background.classList.add('animate');
    window.background.addEventListener('animationend', () => window.background.classList.remove('animate'));
  }

// update the input value
function updateTimeFromInput(type) {
  const input = document.getElementById(`${type}-time`);
  sanitizeInput(input, type); 
}

function formatIsoToDateTimeString(isoString) {
    if (!isoString) return null;
    const date = new Date(isoString);

    const year = date.getUTCFullYear();
    const month = (date.getUTCMonth() + 1).toString().padStart(2, '0'); // Months are 0-indexed
    const day = date.getUTCDate().toString().padStart(2, '0');
    const hours = date.getUTCHours().toString().padStart(2, '0');
    const minutes = date.getUTCMinutes().toString().padStart(2, '0');
    const seconds = date.getUTCSeconds().toString().padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

async function sendStudyDurationToServer(durationMinutes, startTimeIso, endTimeIso,  stopTimesCount) {
    if (durationMinutes <= 0) {
        console.log("Study duration is zero or less, not sending to server.");
        return;
    }
    const formattedStartTime = formatIsoToDateTimeString(startTimeIso);
    const formattedEndTime = formatIsoToDateTimeString(endTimeIso);

    if (!formattedStartTime || !formattedEndTime) {
        console.error("Failed to format date strings. Aborting send.");
        return;
    }

    const requestData = {
        duration: durationMinutes,    // in minutes
        start_time: formattedStartTime, // ISO string
        end_time: formattedEndTime,     // ISO string
        stop_times: stopTimesCount
    };
    console.log("Sending study duration data to /api/studyduration:", requestData);
    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        const response = await fetch('/api/studyduration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Include CSRF token for security
            },
            body: JSON.stringify(requestData)
        });
        const data = await response.json();
        if (response.ok && data.success) {
            console.log('Study duration recorded successfully:', data);
        } else {
            console.error('Failed to record study duration:', data.message || response.statusText);
        }
    } catch (error) {
        console.error("Error sending study duration data:", error);
    }
}
function startTimer() {
  window.pauseCount = 0;
  console.log("start record", { focusTime, breakTime, remainingSeconds });
  updateTimeFromInput('focus');
  updateTimeFromInput('break');

  document.getElementById('setup-area').style.display = 'none';
  document.getElementById('floating-timer').classList.add('show');
 

  if (timer) return;
  
 if (isFocus) {
    currentSessionStartTime = new Date();
    currentSessionInitialFocusTime = focusTime; // Capture the focus time for this session
    pauseCount = 0; // Reset pause count for the new focus session
  } else {
    currentSessionStartTime = null; // Not a focus session, or break session starting
  }
  
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
        // Record end time as ISO string
        const endTime = new Date();
        const endTimeIso = endTime.toISOString();
        sendStudyDurationToServer(currentSessionInitialFocusTime, currentSessionStartTime.toISOString(), endTimeIso,pauseCount);
        showPopup();
        
      }
    }
  }, 1000);
}

function pauseTimer() {
    isPaused = !isPaused;

    const pausePath = document.getElementById('pause-path');
    
    if (isPaused) {
        if (isFocus && currentSessionStartTime) { // Only increment pauseCount during an active focus session
            pauseCount++;
        }        
        pausePath.setAttribute("d", "M22 11v2h-1v1h-1v1h-2v1h-2v1h-1v1h-2v1h-2v1h-1v1H8v1H6v1H3v-1H2V2h1V1h3v1h2v1h2v1h1v1h2v1h2v1h1v1h2v1h2v1h1v1z");
      } else {
        pausePath.setAttribute("d", "M23 2v20h-1v1h-7v-1h-1V2h1V1h7v1zM9 2h1v20H9v1H2v-1H1V2h1V1h7z");
      }
}

function resetTimer() {
  clearInterval(timer);
  timer = null;

  // If a focus session was active, record the time spent before resetting
  if (isFocus && currentSessionStartTime) {
    const elapsedSeconds = (currentSessionInitialFocusTime * 60) - remainingSeconds;
    if (elapsedSeconds > 0) {
        const durationMinutes = Math.round(elapsedSeconds / 60);
        // Record end time as ISO string
        const endTime = new Date();
        const endTimeIso = endTime.toISOString();
        sendStudyDurationToServer(durationMinutes, currentSessionStartTime.toISOString(), endTimeIso, pauseCount);
    }
  }
  
  currentSessionStartTime = null; // Reset session tracking
  isPaused = false;
  remainingSeconds = 0;
  isFocus = true; // Default back to focus mode
  // pauseCount will be reset by startTimer if a new focus session begins
  updateCountdownDisplay();

  document.getElementById('floating-timer').classList.remove('show');
  document.getElementById('setup-area').style.display = 'block';
}

function updateCountdownDisplay() {
  const min = Math.floor(remainingSeconds / 60).toString().padStart(2, '0');
  const sec = (remainingSeconds % 60).toString().padStart(2, '0');
  const emoji = isFocus ? "✍🏻" : "☕";
  const emoji2 = isFocus ? "📖" : "🍫"

  const countdownDisplay = document.getElementById('countdown-display');
if (countdownDisplay) {
  countdownDisplay.textContent = `${emoji} ${min}:${sec} ${emoji2}`;
}

}

function backToSetup() {
  resetTimer();
}

function showPopup() {
  console.log("===== showPopup start run =====");
  try {
    console.log("read varis:", { isFocus, focusTime, breakTime, currentSessionStartTime, currentSessionInitialFocusTime, pauseCount });
    const times = isFocus ? currentSessionInitialFocusTime : breakTime; // Use initial focus time for display
    const formatted = `${String(times).padStart(2, '0')}:00`; 
    const emoji = "🎉";
    console.log("Formatting time:", formatted);
    
    if (isFocus && currentSessionStartTime) {  
      console.log("isFocus = true, sending study duration");
      // Duration is the initially set focus time for the completed session
      currentSessionStartTime = null; // Reset session tracking after recording
    } else {
      console.log("Not a focus session or session already recorded/reset, not sending study duration.");
    }
    
    console.log("DOM updates for popup");
    document.getElementById('completed_time').textContent = `Your Focus Time: ${formatted}`;
    document.getElementById('popup-window').style.display = 'block';
    document.getElementById('floating-timer').classList.remove('show');
    console.log("DOM updates finished");
    
  } catch (error) {
    console.error("showPopup wrong:", error);
  }
  console.log("===== showPopup end =====");
}

function closePopup() {
  document.getElementById('popup-window').style.display='none';
  document.getElementById('setup-area').style.display = 'block';
}

function takeBreak() {
  document.getElementById('popup-window').style.display='none';
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
        document.getElementById('floating-timer').classList.remove('show');
        document.getElementById('break-window').style.display='block';
      }
    }
  }, 1000);
}

function ContinueFocus() {
  isFocus = true;
  remainingSeconds = focusTime * 60;
  document.getElementById('break-window').style.display = 'none';
  document.getElementById('floating-timer').classList.add('show');
  updateCountdownDisplay();

  if (timer) clearInterval (timer);
  
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

// Wrapping all logic in a single function ensures it runs only after the DOM is fully loaded.
// This avoids errors from trying to access elements that don’t yet exist.
function initMainpageFeatures() {
  restoreTimerState();
  restoreBackgroundAndMusic();

  if (!window.timer && window.remainingSeconds > 0) {
    updateCountdownDisplay();
    document.getElementById('setup-area').style.display = 'none';
    document.getElementById('floating-timer').classList.add('show');
    window.timer = setInterval(() => {
      if (!window.isPaused) {
        window.remainingSeconds--;
        updateCountdownDisplay();
        if (window.remainingSeconds <= 0) {
          clearInterval(window.timer);
          window.timer = null;
          showPopup();
        }
      }
    }, 1000);
  }
  
  const isReload = performance.getEntriesByType("navigation")[0].type === "reload";
  
  if (isReload) {
    resetTimer(); 
    console.log("refresh page, timer state reset");
  } else {
    console.log("page loaded, timer state preserved");
    if (remainingSeconds > 0 && !timer) {
      updateCountdownDisplay();
      document.getElementById('setup-area').style.display = 'none';
      document.getElementById('floating-timer').classList.add('show');
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
  }

['focus', 'break'].forEach(type => {
  const input = document.getElementById(`${type}-time`);
  if (input) input.addEventListener('input', () => sanitizeInput(input, type));
});

document.getElementById('focus-minus')?.addEventListener('click', () => adjustTime('focus', -1));
document.getElementById('focus-plus')?.addEventListener('click', () => adjustTime('focus', 1));
document.getElementById('break-minus')?.addEventListener('click', () => adjustTime('break', -1));
document.getElementById('break-plus')?.addEventListener('click', () => adjustTime('break', 1));
document.getElementById('start-btn')?.addEventListener('click', startTimer);
document.getElementById('pause-btn')?.addEventListener('click', pauseTimer);
document.getElementById('reset-btn')?.addEventListener('click', resetTimer);
document.getElementById('break-btn')?.addEventListener('click', takeBreak);
document.getElementById('continue-btn')?.addEventListener('click', ContinueFocus);
document.querySelectorAll('#close-btn').forEach(btn => {
  btn.addEventListener('click', closePopup);
});

 /* Goal setting widget JS (Task List) */
    const taskInput = document.getElementById('task-input');
    const addBtn = document.getElementById('add-btn');
    const taskList = document.querySelector('.task-list');
    const filters = document.querySelectorAll('.filter');

    // --- Helper function to create a task list item ---
    function createTaskElement(task) {
        const li = document.createElement('li');
        li.className = 'task';
        // Use studyplan's status: 0 for active/open, 1 for completed
        li.setAttribute('data-status', task.status === 1 ? 'completed' : 'active');
        li.setAttribute('data-id', task.id); // Store the task ID from the backend

        li.innerHTML = `
            <div class="task-content">
                <input type="checkbox" class="task-checkbox" ${task.status === 1 ? 'checked' : ''} />
                <span class="task-text ${task.status === 1 ? 'completed' : ''}">${task.content}</span>
                <button class="expand-btn">${icon_down}</button>
                <button class="delete-btn">${icon_delete}</button>
            </div>
        `;
        return li;
    }

    // --- Load tasks from the backend (Study Plans with status 0 or 1) ---
    function loadTasks() {
        taskList.innerHTML = ''; // Clear existing tasks
        // Fetch non-deleted study plans (status 0: open, status 1: completed)
        // The API /api/studyplan by default excludes status 2 (deleted)
        fetch('/api/studyplan')
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                if (data.success && data.study_plans) {
                    data.study_plans.forEach(plan => {
                        const li = createTaskElement(plan);
                        taskList.appendChild(li);
                    });
                    applyCurrentFilter(); // Re-apply filter after loading
                } else {
                    console.warn("Could not load tasks:", data.message);
                }
            })
            .catch(error => {
                console.error("Error fetching tasks:", error);
                taskList.innerHTML = '<li>Error loading tasks. Please try again.</li>';
            });
    }

    // --- Add Task (Study Plan) ---
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            const taskText = taskInput.value.trim();
            if (taskText === '') return;
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

            // POST to studyplan API
            fetch('/api/studyplan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // Include CSRF token for security
                },
                body: JSON.stringify({ content: taskText }) // 'content' matches StudyPlan model
            })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(err => { throw new Error(err.message || `HTTP error! status: ${res.status}`) });
                }
                return res.json();
            })
            .then(data => {
                if (data.success && data.study_plan) {
                    const li = createTaskElement(data.study_plan);
                    taskList.appendChild(li);
                    taskInput.value = '';
                    applyCurrentFilter(); // Apply current filter to new task
                } else {
                    console.warn("Failed to add task:", data.message);
                    alert("Error: " + (data.message || "Could not add task."));
                }
            })
            .catch(error => {
                console.error("Error adding task:", error);
                alert("Error: " + error.message);
            });
        });
    }

    // --- Handle Checkbox Toggle (Update Task Status) and Delete Task ---
    if (taskList) {
        taskList.addEventListener('click', e => { // Changed from 'change' to 'click' for checkboxes for better responsiveness
            const target = e.target;

            // --- Checkbox Toggle ---
            if (target.classList.contains('task-checkbox')) {
                const taskElement = target.closest('li.task');
                const taskId = taskElement.dataset.id;
                const isChecked = target.checked;
                const newStatus = isChecked ? 1 : 0; // 1 for completed, 0 for open
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

                fetch(`/api/studyplan/${taskId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken // Include CSRF token for security
                    },
                    body: JSON.stringify({ status: newStatus })
                })
                .then(res => {
                    if (!res.ok) {
                        // Roll back checkbox if request fails
                        target.checked = !isChecked;
                        return res.json().then(err => { throw new Error(err.message || `HTTP error! status: ${res.status}`) });
                    }
                    return res.json();
                })
                .then(data => {
                    if (data.success && data.study_plan) {
                        taskElement.setAttribute('data-status', newStatus === 1 ? 'completed' : 'active');
                        taskElement.querySelector('.task-text').classList.toggle('completed', newStatus === 1);
                        applyCurrentFilter(); // Re-apply filter to show/hide task if necessary
                    } else {
                        console.warn("Failed to update task status:", data.message);
                        alert("Error: " + (data.message || "Could not update task."));
                        target.checked = !isChecked; // Roll back checkbox
                    }
                })
                .catch(error => {
                    console.error("Error updating task status:", error);
                    alert("Error: " + error.message);
                    target.checked = !isChecked; // Roll back checkbox
                });
            }

            // --- Delete Task ---
            const deleteButton = target.closest('.delete-btn');
            if (deleteButton) {
                const taskElement = deleteButton.closest('li.task');
                const taskId = taskElement.dataset.id;
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

                if (confirm('Are you sure you want to delete this task?')) {
                    fetch(`/api/studyplan/${taskId}`, {
                        method: 'DELETE',
                        headers: {
                          'X-CSRFToken': csrfToken // Include CSRF token for security
                        }
                    })
                    .then(res => {
                        if (!res.ok) {
                             return res.json().then(err => { throw new Error(err.message || `HTTP error! status: ${res.status}`) });
                        }
                        return res.json();
                    })
                    .then(data => {
                        if (data.success) {
                            taskElement.remove();
                        } else {
                            console.warn("Failed to delete task:", data.message);
                            alert("Error: " + (data.message || "Could not delete task."));
                        }
                    })
                    .catch(error => {
                        console.error("Error deleting task:", error);
                        alert("Error: " + error.message);
                    });
                }
            }

            // --- Expand Button (existing logic) ---
            const expandBtn = target.closest('.expand-btn');
            if (expandBtn) {
                const task = expandBtn.closest('.task');
                task.classList.toggle('expanded');
                expandBtn.innerHTML = task.classList.contains('expanded') ? icon_up : icon_down;
            }
        });
    }

    // --- Filter Tasks ---
    function applyCurrentFilter() {
        const activeFilterButton = document.querySelector('.filter.active');
        if (activeFilterButton) {
            const filterType = activeFilterButton.getAttribute('data-filter');
            document.querySelectorAll('.task-list .task').forEach(task => {
                const status = task.getAttribute('data-status');
                if (filterType === 'all') {
                    task.style.display = 'flex';
                } else {
                    task.style.display = status === filterType ? 'flex' : 'none';
                }
            });
        }
    }

    if (filters) {
        filters.forEach(button => {
            button.addEventListener('click', () => {
                const currentActive = document.querySelector('.filter.active');
                if (currentActive) {
                    currentActive.classList.remove('active');
                }
                button.classList.add('active');
                applyCurrentFilter();
            });
        });
    }

    // --- Toggle Task List Visibility (existing logic) ---
    const toggleListBtn = document.getElementById('toggle-task-list');
    const taskListContainer = document.querySelector('.task-list'); // Ensure correct selector for task list

    if (toggleListBtn && taskListContainer) {
        toggleListBtn.addEventListener('click', () => {
            taskListContainer.classList.toggle('hidden');
            toggleListBtn.textContent = taskListContainer.classList.contains('hidden')
                ? 'Show' 
                : 'Hide';
        });
    }

    // --- Icons (existing logic) ---
    const icon_up = `
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24 ">
      <path fill="#fff" d="M20 15v1h-1v1h-1v-1h-1v-1h-1v-1h-1v-1h-1v-1h-2v1h-1v1H9v1H8v1H7v1H6v1H5v-1H4v-1h1v-1h1v-1h1v-1h1v-1h1v-1h1V9h1V8h2v1h1v1h1v1h1v1h1v1h1v1h1v1z" />
    </svg>`;

    const icon_down = `
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24">
      <path fill="#fff" d="M20 8v1h-1v1h-1v1h-1v1h-1v1h-1v1h-1v1h-1v1h-2v-1h-1v-1H9v-1H8v-1H7v-1H6v-1H5V9H4V8h1V7h1v1h1v1h1v1h1v1h1v1h1v1h2v-1h1v-1h1v-1h1V9h1V8h1V7h1v1z" />
    </svg>`;

    const icon_delete = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24">
    <path fill="#fff" d="M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6zM8 9h8v10H8zm7.5-5l-1-1h-5l-1 1H5v2h14V4z" />
    </svg>`;

    // --- Initial Load of Tasks ---
    loadTasks();

taskList.addEventListener('click', e => {
  const expandBtn = e.target.closest('.expand-btn');
  if (expandBtn) {
    const task = expandBtn.closest('.task');
    task.classList.toggle('expanded');
    expandBtn.innerHTML = task.classList.contains('expanded') ? icon_up : icon_down;
  }

  const deleteBtn = e.target.closest('.delete-btn');
  if (deleteBtn) {
    const task = deleteBtn.closest('.task');
    task.remove();
  }

});

/* Background widget JS */
    const bgDiv = document.getElementById('bg-gif');
    const bgSelect = document.getElementById('bg-select');
    const musicSelect = document.getElementById('music-select');
    const audio = document.getElementById('bg-audio');
    const volumeSlider = document.getElementById('volume-range');
    const toggleMuteBtn = document.getElementById('toggle-mute');
    
    let lastVolume = 0.3; // default volume when unmuted
    
    // initial setup - mute the audio and set volume to 0
    audio.muted = true;
    audio.volume = 0;
    volumeSlider.value = 0;
    toggleMuteBtn.textContent = 'Unmute';
    
    // background change
    bgSelect.addEventListener('change', () => {
      bgDiv.style.backgroundImage = `url('/static/gifs/${bgSelect.value}')`;
  localStorage.setItem('bgSelected', bgSelect.value); 
    });

    // music change
    musicSelect.addEventListener('change', () => {
      audio.src =  `/static/audio/${musicSelect.value}`;
  localStorage.setItem('musicSelected', musicSelect.value); 
      if (!audio.muted) {
        audio.play().catch(err => console.warn("Autoplay restriction:", err));
      }
    });
    
    // volume change
  volumeSlider.addEventListener('input', () => {
    const vol = parseFloat(volumeSlider.value);
    audio.volume = vol;
    localStorage.setItem('volume', audio.volume); 
    localStorage.setItem('muted', audio.muted); 
    
      if (vol === 0) {
        audio.muted = true;
        toggleMuteBtn.textContent = 'Unmute';
      } else {
        lastVolume = vol; // Remember user-set volume
        audio.muted = false;
        toggleMuteBtn.textContent = 'Mute';

        // Ensure audio playback if not muted
        if (audio.paused) {
        audio.play().catch(err => console.warn("Autoplay blocked:", err));
    }

    lastVolume = vol;
      }
    });
    
    // Mute and store last volume
    toggleMuteBtn.addEventListener('click', () => {
      if (audio.muted) {
        // Unmute and restore volume
        audio.muted = false;
        audio.volume = lastVolume;
        volumeSlider.value = lastVolume;
        audio.play().catch(err => console.warn("Autoplay restriction:", err));
        toggleMuteBtn.textContent = 'Mute';
      } else {
        // Mute and store last volume
        lastVolume = audio.volume;
        audio.muted = true;
        audio.volume = 0;
        volumeSlider.value = 0;
        toggleMuteBtn.textContent = 'Unmute';
      }
    });

const isFirstLoad = window.name !== '__initialized__';
if (isFirstLoad) {
  window.name = '__initialized__'; // Mark page as initialized
  window.focusTime = 50;
  window.breakTime = 10;
  window.remainingSeconds = 0;
  window.isFocus = true;
  window.isPaused = false;
  window.timer = null;
  console.log("refresh page, timer initialized");
} else {
  console.log("refresh page, timer state preserved");
}

function restoreBackgroundAndMusic() {
  const bgDiv = document.getElementById('bg-gif');
  const bgSelect = document.getElementById('bg-select');
  const musicSelect = document.getElementById('music-select');
  const audio = document.getElementById('bg-audio');
  const volumeSlider = document.getElementById('volume-range');
  const toggleMuteBtn = document.getElementById('toggle-mute');

  if (!bgDiv || !bgSelect || !musicSelect || !audio || !volumeSlider || !toggleMuteBtn) {
    console.warn("restoreBackgroundAndMusic: DOM elements not loaded yet, skipping restoration.");
    return;
  }

  const savedBg = localStorage.getItem('bgSelected');
  if (savedBg) {
    bgDiv.style.backgroundImage = `url('/static/gifs/${savedBg}')`;
    bgSelect.value = savedBg;
  }

  const savedMusic = localStorage.getItem('musicSelected');
  if (savedMusic) {
    audio.src = `/static/audio/${savedMusic}`;
    musicSelect.value = savedMusic;
  }

  const savedVolume = parseFloat(localStorage.getItem('volume'));
  if (!isNaN(savedVolume)) {
    audio.volume = savedVolume;
    volumeSlider.value = savedVolume;
  }

  const savedMuted = localStorage.getItem('muted') === 'true';
  audio.muted = savedMuted;
  toggleMuteBtn.textContent = savedMuted ? 'Unmute' : 'Mute';
}

}


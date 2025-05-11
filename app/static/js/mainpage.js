/* Timer widget JS */
// Initialise the default value
// (function () {
let focusTime = 50;
let breakTime = 10;
let remainingSeconds = 0;
let isFocus = true;
let isPaused = false;
let timer = null;
// })();




    // Restricting the minimum and maximum input value (if the input value is less than 1, then change to 1; if is more than 180, then change to 1)
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
    // Because 'getElementById' method always returns string, therefore, use ParseInt() to change it into integer
    let value = parseInt(input.value, 10);
    if (isNaN(value)) return;
    setTimeValue(type, value);
  }
  
  
  const setupArea = document.getElementById('setup-area');
  if (setupArea) {
    setupArea.classList.add('animate');
    setupArea.addEventListener('animationend', () => setupArea.classList.remove('animate'));
  }
  
  const todoContainer = document.getElementById('todo-container');
  if (todoContainer) {
    todoContainer.classList.add('animate');
    todoContainer.addEventListener('animationend', () => todoContainer.classList.remove('animate'));
  }
  

  // TODO: ✅ GET: Load the task data from the backend and display it in the task list
  fetch('/api/dashboard/task')
  .then(res => res.json())
  .then(tasks => {
    tasks.forEach(task => {
      const li = document.createElement('li');
      li.className = 'task';
      li.setAttribute('data-status', task.status === 1 ? 'completed' : 'active');
      li.setAttribute('data-id', task.id);
      li.innerHTML = `
        <div class="task-content">
          <input type="checkbox" class="task-checkbox" ${task.status === 1 ? 'checked' : ''} />
          <span class="task-text ${task.status === 1 ? 'completed' : ''}">${task.title}</span>
          <button class="expand-btn">${icon_down}</button>
          <button class="delete-btn">${icon_delete}</button>
        </div>
      `;
      taskList.appendChild(li);
    });
  });

// update the input value
function updateTimeFromInput(type) {
  const input = document.getElementById(`${type}-time`);
  sanitizeInput(input, type); 
}

function startTimer() {
  console.log("start record", { focusTime, breakTime, remainingSeconds });
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
  const emoji = isFocus ? "✍🏻" : "☕";
  const emoji2 = isFocus ? "📖" : "🍫"

  document.getElementById('countdown-display').textContent = `${emoji} ${min}:${sec} ${emoji2}`;
}

function backToSetup() {
  resetTimer();
}


// function showPopup() {
//   console.log("showPopup", { isFocus, focusTime, breakTime });
//   const times = isFocus ? focusTime : breakTime;
//   const formatted = `${String(times).padStart(2, '0')}:00`; 
//   const emoji = "🎉"

//   document.getElementById('completed_time').textContent = `Your Focus Time: ${formatted}`;
//   document.getElementById('popup-window').style.display = 'block';
//   document.getElementById('floating-timer').classList.remove('show');

// }

function showPopup() {
  console.log("===== showPopup start run =====");
  try {
    console.log("read varis:", { isFocus, focusTime, breakTime });
    const times = isFocus ? focusTime : breakTime;
    const formatted = `${String(times).padStart(2, '0')}:00`; 
    const emoji = "🎉";
    console.log("Formatting time:", formatted);
    
    // 添加发送学习时间数据的代码
    if (isFocus) {  
      console.log("isforce = ture send");
      const requestData = { 
        duration: focusTime,
        start_time: new Date().toISOString()
      };
      console.log("require:", requestData);
      
      try {
        console.log("fetch send ...");
        fetch('/api/study_time', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })
        .then(response => {
          console.log("receive response:", response.status, response.statusText);
          return response.json();
        })
        .then(data => {
          console.log('API:', data);
        })
        .catch(err => {
          console.error("fetch process wrong:", err);
        });
        console.log("fetch send");
      } catch (fetchError) {
        console.error("fetch wrong:", fetchError);
      }
    } else {
      console.log("isFocus=false，dont send");
    }
    
    console.log("DOM");
    document.getElementById('completed_time').textContent = `Your Focus Time: ${formatted}`;
    document.getElementById('popup-window').style.display = 'block';
    document.getElementById('floating-timer').classList.remove('show');
    console.log("DOM finished");
    
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

            // POST to studyplan API
            fetch('/api/studyplan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add CSRF token header if your app uses it for POST/PUT/DELETE
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
                    applyCurrentFilter(); // Apply filter to new task
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

                fetch(`/api/studyplan/${taskId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        // Add CSRF token header if needed
                    },
                    body: JSON.stringify({ status: newStatus })
                })
                .then(res => {
                    if (!res.ok) {
                        // Revert checkbox on error before throwing
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
                        target.checked = !isChecked; // Revert checkbox
                    }
                })
                .catch(error => {
                    console.error("Error updating task status:", error);
                    alert("Error: " + error.message);
                    target.checked = !isChecked; // Revert checkbox
                });
            }

            // --- Delete Task ---
            const deleteButton = target.closest('.delete-btn');
            if (deleteButton) {
                const taskElement = deleteButton.closest('li.task');
                const taskId = taskElement.dataset.id;

                if (confirm('Are you sure you want to delete this task?')) {
                    fetch(`/api/studyplan/${taskId}`, {
                        method: 'DELETE',
                        headers: {
                            // Add CSRF token header if needed
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
    const taskListContainer = document.querySelector('.task-list'); // Ensure this selector is correct

    if (toggleListBtn && taskListContainer) {
        toggleListBtn.addEventListener('click', () => {
            taskListContainer.classList.toggle('hidden');
            toggleListBtn.textContent = taskListContainer.classList.contains('hidden')
                ? 'Show Tasks' // Or your preferred text
                : 'Hide Tasks'; // Or your preferred text
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
    
    // 背景切换
    bgSelect.addEventListener('change', () => {
      bgDiv.style.backgroundImage = `url('/static/gifs/${bgSelect.value}')`;
    });
    
    // 音乐切换
    musicSelect.addEventListener('change', () => {
      audio.src =  `/static/audio/${musicSelect.value}`;
      if (!audio.muted) {
        audio.play().catch(err => console.warn("Autoplay restriction:", err));
      }
    });
    
    // 音量调节
    volumeSlider.addEventListener('input', () => {
      const vol = parseFloat(volumeSlider.value);
      audio.volume = vol;
    
      if (vol === 0) {
        audio.muted = true;
        toggleMuteBtn.textContent = 'Unmute';
      } else {
        lastVolume = vol; // 记住用户设置的音量
        audio.muted = false;
        toggleMuteBtn.textContent = 'Mute';

        // ensure audio plays if not muted
        if (audio.paused) {
        audio.play().catch(err => console.warn("Autoplay blocked:", err));
    }

    lastVolume = vol;
      }
    });
    
    // 静音切换按钮
    toggleMuteBtn.addEventListener('click', () => {
      if (audio.muted) {
        // 取消静音：恢复上次音量
        audio.muted = false;
        audio.volume = lastVolume;
        volumeSlider.value = lastVolume;
        audio.play().catch(err => console.warn("Autoplay restriction:", err));
        toggleMuteBtn.textContent = 'Mute';
      } else {
        // 静音：记住当前音量并设为0
        lastVolume = audio.volume;
        audio.muted = true;
        audio.volume = 0;
        volumeSlider.value = 0;
        toggleMuteBtn.textContent = 'Unmute';
      }
    });

    window.addEventListener('DOMContentLoaded', () => {
    const background = document.getElementById('audio-widget');
    if (background) {
    background.classList.add('animate');
    background.addEventListener('animationend', () => {
      background.classList.remove('animate');
    });
  } 
    
}); 


}
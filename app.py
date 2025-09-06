#!/usr/bin/env python3
"""
HealthyLife Pro - Complete Working Web Application
Run this file and go to http://localhost:5000
"""

from flask import Flask, request, jsonify, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'healthylife-secret-key-2024'

# Simple in-memory storage
users_data = {}

def get_user_data():
    """Get current user's data"""
    user_id = session.get('user_id', 'demo_user')
    session['user_id'] = user_id
    
    if user_id not in users_data:
        users_data[user_id] = {
            'water_count': 0,
            'habits': {
                'meditation': False,
                'exercise': False,
                'reading': False,
                'water_intake': False,
                'healthy_eating': False
            },
            'meals': [],
            'exercises': [],
            'sleep_data': {},
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
    
    # Reset data if it's a new day
    today = datetime.now().strftime('%Y-%m-%d')
    if users_data[user_id]['last_updated'] != today:
        users_data[user_id].update({
            'water_count': 0,
            'habits': {k: False for k in users_data[user_id]['habits']},
            'meals': [],
            'exercises': [],
            'sleep_data': {},
            'last_updated': today
        })
    
    return users_data[user_id]

def generate_water_glasses(water_count):
    """Generate water glass HTML"""
    glasses = []
    for i in range(8):
        filled_class = "filled" if i < water_count else ""
        glasses.append(f'<div class="water-glass {filled_class}" onclick="toggleWaterGlass({i})">{i+1}</div>')
    return ''.join(glasses)

def generate_habit_items(habits):
    """Generate habit items HTML"""
    items = []
    for habit_name, completed in habits.items():
        checked_class = "checked" if completed else ""
        check_mark = "✓" if completed else ""
        habit_display = habit_name.replace('_', ' ').title()
        items.append(f'''
        <div class="habit-item">
            <span>{habit_display}</span>
            <div class="habit-checkbox {checked_class}" onclick="toggleHabit('{habit_name}')">
                {check_mark}
            </div>
        </div>
        ''')
    return ''.join(items)

def generate_meal_items(meals):
    """Generate meal items HTML"""
    if not meals:
        return '<p>No meals logged today. Start by adding your first meal!</p>'
    
    items = []
    for meal in meals:
        items.append(f'''
        <div class="meal-item">
            <h4>{meal["type"].title()} ({meal["timestamp"]})</h4>
            <p><strong>Items:</strong> {meal["items"]}</p>
            <p><strong>Calories:</strong> {meal["calories"]}</p>
        </div>
        ''')
    return ''.join(items)

def generate_exercise_items(exercises):
    """Generate exercise items HTML"""
    if not exercises:
        return '<p>No exercises logged today. Time to get moving!</p>'
    
    items = []
    for exercise in exercises:
        items.append(f'''
        <div class="exercise-item">
            <h4>{exercise["name"]} ({exercise["timestamp"]})</h4>
            <p><strong>Duration:</strong> {exercise["duration"]} minutes</p>
            <p><strong>Calories Burned:</strong> {exercise["calories"]}</p>
        </div>
        ''')
    return ''.join(items)

@app.route('/')
def index():
    """Main page with embedded HTML, CSS, and JavaScript"""
    data = get_user_data()
    
    # Calculate statistics
    water_progress = int(data['water_count'] / 8 * 100)
    exercise_calories = sum(ex.get('calories', 0) for ex in data['exercises'])
    activity_progress = min(int(exercise_calories / 500 * 100), 100)
    nutrition_progress = min(int(len(data['meals']) / 3 * 100), 100)
    meal_calories = sum(meal.get('calories', 0) for meal in data['meals'])
    
    completed_habits = sum(1 for v in data['habits'].values() if v)
    total_habits = len(data['habits'])
    habit_completion = int(completed_habits / total_habits * 100) if total_habits > 0 else 0
    
    sleep_progress = 0
    sleep_display = 'No data'
    if data['sleep_data'].get('duration'):
        sleep_progress = min(int(data['sleep_data']['duration'] / 8 * 100), 100)
        sleep_display = f"{data['sleep_data']['duration']}h (Quality: {data['sleep_data']['quality']}/10)"
    
    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌟 HealthyLife Pro</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }}

        header h1 {{
            font-size: 3.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: glow 2s ease-in-out infinite alternate;
        }}

        @keyframes glow {{
            from {{ text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
            to {{ text-shadow: 2px 2px 20px rgba(255,255,255,0.5); }}
        }}

        .nav-tabs {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 30px;
        }}

        .tab-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 15px 30px;
            cursor: pointer;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}

        .tab-btn:hover, .tab-btn.active {{
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.8);
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}

        .tab-content {{
            display: none;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
        }}

        .tab-content.active {{
            display: block;
            animation: slideIn 0.6s ease;
        }}

        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}

        .card {{
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}

        .card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
        }}

        .card h3 {{
            color: #4a5568;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}

        .progress-container {{
            margin: 15px 0;
        }}

        .progress-bar {{
            width: 100%;
            height: 12px;
            background: #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 6px;
            transition: width 0.8s ease;
        }}

        .water-tracker {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 15px;
            justify-content: center;
        }}

        .water-glass {{
            width: 40px;
            height: 60px;
            background: #e2e8f0;
            border-radius: 0 0 20px 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 3px solid #667eea;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            color: #667eea;
            font-weight: bold;
            font-size: 12px;
            padding-bottom: 5px;
        }}

        .water-glass:hover {{
            transform: scale(1.1);
        }}

        .water-glass.filled {{
            background: linear-gradient(to top, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}

        .habit-item {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-bottom: 15px;
        }}

        .habit-checkbox {{
            width: 30px;
            height: 30px;
            border: 2px solid #667eea;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            font-size: 18px;
            font-weight: bold;
        }}

        .habit-checkbox.checked {{
            background: #667eea;
            color: white;
        }}

        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.6);
        }}

        .input-group {{
            margin-bottom: 20px;
        }}

        .input-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #4a5568;
        }}

        .input-group input, .input-group select, .input-group textarea {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }}

        .input-group input:focus, .input-group select:focus, .input-group textarea:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 20px;
            text-align: center;
        }}

        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #48bb78;
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1000;
        }}

        .notification.show {{
            transform: translateX(0);
        }}

        .notification.error {{
            background: #e53e3e;
        }}

        .meal-item, .exercise-item {{
            background: rgba(255, 255, 255, 0.7);
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}

        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            header h1 {{ font-size: 2.5rem; }}
            .tab-content {{ padding: 20px; }}
            .dashboard-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌟 HealthyLife Pro</h1>
            <p>Your AI-powered wellness companion with real-time tracking</p>
        </header>

        <div class="nav-tabs">
            <button class="tab-btn active" onclick="showTab('dashboard')">📊 Dashboard</button>
            <button class="tab-btn" onclick="showTab('habits')">✅ Habits</button>
            <button class="tab-btn" onclick="showTab('nutrition')">🍎 Nutrition</button>
            <button class="tab-btn" onclick="showTab('exercise')">💪 Exercise</button>
            <button class="tab-btn" onclick="showTab('sleep')">😴 Sleep</button>
            <button class="tab-btn" onclick="showTab('analytics')">📈 Analytics</button>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="dashboard-grid">
                <div class="card">
                    <h3>💧 Hydration Tracker</h3>
                    <p><strong>Today's Goal:</strong> <span id="water-count">{data['water_count']}</span>/8 glasses</p>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div id="water-progress" class="progress-fill" style="width: {water_progress}%"></div>
                        </div>
                    </div>
                    <div class="water-tracker" id="water-glasses">
                        {generate_water_glasses(data['water_count'])}
                    </div>
                </div>

                <div class="card">
                    <h3>🎯 Today's Habits</h3>
                    <div id="habit-summary">
                        {generate_habit_items(data['habits'])}
                    </div>
                </div>

                <div class="card">
                    <h3>🏃‍♂️ Activity Overview</h3>
                    <p><strong>Exercises Today:</strong> <span id="exercise-count">{len(data['exercises'])}</span></p>
                    <p><strong>Total Calories Burned:</strong> <span id="calories-burned">{exercise_calories}</span></p>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div id="activity-progress" class="progress-fill" style="width: {activity_progress}%"></div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>🍽️ Nutrition Summary</h3>
                    <p><strong>Meals Logged:</strong> <span id="meals-count">{len(data['meals'])}</span>/3</p>
                    <p><strong>Calories Consumed:</strong> <span id="calories-consumed">{meal_calories}</span></p>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div id="nutrition-progress" class="progress-fill" style="width: {nutrition_progress}%"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Habits Tab -->
        <div id="habits" class="tab-content">
            <div class="card">
                <h3>✅ Daily Habits Tracker</h3>
                <div id="habits-list">
                    {generate_habit_items(data['habits'])}
                </div>
                <div style="margin-top: 30px;">
                    <div class="input-group">
                        <label>Add New Habit:</label>
                        <input type="text" id="new-habit" placeholder="Enter habit name">
                    </div>
                    <button class="btn" onclick="addNewHabit()">Add Habit</button>
                </div>
            </div>
        </div>

        <!-- Nutrition Tab -->
        <div id="nutrition" class="tab-content">
            <div class="dashboard-grid">
                <div class="card">
                    <h3>🍽️ Meal Logger</h3>
                    <div class="input-group">
                        <label>Meal Type:</label>
                        <select id="meal-type">
                            <option value="breakfast">Breakfast</option>
                            <option value="lunch">Lunch</option>
                            <option value="dinner">Dinner</option>
                            <option value="snack">Snack</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Food Items:</label>
                        <textarea id="meal-items" placeholder="List the foods you ate" rows="3"></textarea>
                    </div>
                    <div class="input-group">
                        <label>Estimated Calories:</label>
                        <input type="number" id="meal-calories" placeholder="Enter calories">
                    </div>
                    <button class="btn" onclick="logMeal()">Log Meal</button>
                </div>

                <div class="card">
                    <h3>📊 Today's Nutrition</h3>
                    <div id="todays-meals">
                        {generate_meal_items(data['meals'])}
                    </div>
                </div>
            </div>
        </div>

        <!-- Exercise Tab -->
        <div id="exercise" class="tab-content">
            <div class="dashboard-grid">
                <div class="card">
                    <h3>💪 Exercise Logger</h3>
                    <div class="input-group">
                        <label>Exercise Name:</label>
                        <input type="text" id="exercise-name" placeholder="e.g., Running, Push-ups">
                    </div>
                    <div class="input-group">
                        <label>Duration (minutes):</label>
                        <input type="number" id="exercise-duration" placeholder="Enter duration">
                    </div>
                    <div class="input-group">
                        <label>Calories Burned:</label>
                        <input type="number" id="exercise-calories" placeholder="Estimated calories">
                    </div>
                    <button class="btn" onclick="logExercise()">Log Exercise</button>
                </div>

                <div class="card">
                    <h3>🏃‍♂️ Today's Workouts</h3>
                    <div id="todays-exercises">
                        {generate_exercise_items(data['exercises'])}
                    </div>
                </div>
            </div>
        </div>

        <!-- Sleep Tab -->
        <div id="sleep" class="tab-content">
            <div class="card">
                <h3>😴 Sleep Tracker</h3>
                <div class="dashboard-grid">
                    <div>
                        <div class="input-group">
                            <label>Bedtime:</label>
                            <input type="time" id="bedtime">
                        </div>
                        <div class="input-group">
                            <label>Wake Time:</label>
                            <input type="time" id="wake-time">
                        </div>
                        <div class="input-group">
                            <label>Sleep Quality (1-10): <span id="quality-value">7</span></label>
                            <input type="range" id="sleep-quality" min="1" max="10" value="7" oninput="updateQualityValue(this.value)">
                        </div>
                        <button class="btn" onclick="logSleep()">Log Sleep</button>
                    </div>
                    <div>
                        <h4>Sleep Statistics</h4>
                        <p><strong>Last Night:</strong> <span id="last-sleep">{sleep_display}</span></p>
                        <div class="progress-container">
                            <div class="progress-bar">
                                <div id="sleep-progress" class="progress-fill" style="width: {sleep_progress}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Analytics Tab -->
        <div id="analytics" class="tab-content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{data['water_count']}</div>
                    <div class="stat-label">Daily Water (glasses)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{1 if data['exercises'] else 0}</div>
                    <div class="stat-label">Exercise Days Today</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{habit_completion}%</div>
                    <div class="stat-label">Habit Completion Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{exercise_calories}</div>
                    <div class="stat-label">Total Calories Burned</div>
                </div>
            </div>
        </div>
    </div>

    <div class="notification" id="notification"></div>

    <script>
        let currentData = {json.dumps(data)};

        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        function toggleWaterGlass(index) {{
            if (index < currentData.water_count) {{
                currentData.water_count = index;
            }} else {{
                currentData.water_count = index + 1;
            }}
            
            updateWaterDisplay();
            
            fetch('/api/water', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{count: currentData.water_count}})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success && currentData.water_count >= 8) {{
                    showNotification('🎉 Congratulations! You have reached your daily water goal!');
                }}
            }});
        }}

        function updateWaterDisplay() {{
            document.getElementById('water-count').textContent = currentData.water_count;
            document.getElementById('water-progress').style.width = (currentData.water_count / 8 * 100) + '%';
            
            const glasses = document.querySelectorAll('.water-glass');
            glasses.forEach((glass, index) => {{
                if (index < currentData.water_count) {{
                    glass.classList.add('filled');
                }} else {{
                    glass.classList.remove('filled');
                }}
            }});
        }}

        function toggleHabit(habitName) {{
            currentData.habits[habitName] = !currentData.habits[habitName];
            
            const checkboxes = document.querySelectorAll('[onclick*="' + habitName + '"]');
            checkboxes.forEach(checkbox => {{
                if (currentData.habits[habitName]) {{
                    checkbox.classList.add('checked');
                    checkbox.textContent = '✓';
                }} else {{
                    checkbox.classList.remove('checked');
                    checkbox.textContent = '';
                }}
            }});
            
            fetch('/api/habits', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(currentData.habits)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success && currentData.habits[habitName]) {{
                    showNotification('✅ Great job completing: ' + habitName.replace('_', ' ') + '!');
                }}
            }});
        }}

        function addNewHabit() {{
            const input = document.getElementById('new-habit');
            const habitName = input.value.trim().toLowerCase().replace(/\\s+/g, '_');
            
            if (habitName && !currentData.habits[habitName]) {{
                currentData.habits[habitName] = false;
                input.value = '';
                
                fetch('/api/habits', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(currentData.habits)
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        showNotification('New habit added: ' + habitName.replace('_', ' ') + '!');
                        location.reload();
                    }}
                }});
            }} else if (currentData.habits[habitName]) {{
                showNotification('Habit already exists!', 'error');
            }}
        }}

        function logMeal() {{
            const mealType = document.getElementById('meal-type').value;
            const mealItems = document.getElementById('meal-items').value.trim();
            const mealCalories = parseInt(document.getElementById('meal-calories').value);
            
            if (!mealItems || !mealCalories) {{
                showNotification('Please fill in all meal information', 'error');
                return;
            }}
            
            fetch('/api/meals', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    type: mealType,
                    items: mealItems,
                    calories: mealCalories
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    showNotification(mealType.charAt(0).toUpperCase() + mealType.slice(1) + ' logged successfully!');
                    document.getElementById('meal-items').value = '';
                    document.getElementById('meal-calories').value = '';
                    location.reload();
                }}
            }});
        }}

        function logExercise() {{
            const name = document.getElementById('exercise-name').value.trim();
            const duration = parseInt(document.getElementById('exercise-duration').value);
            const calories = parseInt(document.getElementById('exercise-calories').value);
            
            if (!name || !duration || !calories) {{
                showNotification('Please fill in all exercise information', 'error');
                return;
            }}
            
            fetch('/api/exercises', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    name: name,
                    duration: duration,
                    calories: calories
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    showNotification('Exercise "' + name + '" logged successfully!');
                    document.getElementById('exercise-name').value = '';
                    document.getElementById('exercise-duration').value = '';
                    document.getElementById('exercise-calories').value = '';
                    location.reload();
                }}
            }});
        }}

        function updateQualityValue(value) {{
            document.getElementById('quality-value').textContent = value;
        }}

        function logSleep() {{
            const bedtime = document.getElementById('bedtime').value;
            const wakeTime = document.getElementById('wake-time').value;
            const quality = parseInt(document.getElementById('sleep-quality').value);
            
            if (!bedtime || !wakeTime) {{
                showNotification('Please enter both bedtime and wake time', 'error');
                return;
            }}
            
            fetch('/api/sleep', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    bedtime: bedtime,
                    wake_time: wakeTime,
                    quality: quality
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    showNotification('Sleep logged: ' + data.sleep_data.duration + 'h with quality ' + quality + '/10');
                    location.reload();
                }} else {{
                    showNotification(data.error || 'Error logging sleep', 'error');
                }}
            }});
        }}

        function showNotification(message, type = 'success') {{
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = 'notification ' + type;
            notification.classList.add('show');
            
            setTimeout(() => {{
                notification.classList.remove('show');
            }}, 3000);
        }}
    </script>
</body>
</html>
'''
    return html_content

@app.route('/api/water', methods=['POST'])
def update_water():
    """Update water count"""
    data = get_user_data()
    request_data = request.json
    data['water_count'] = request_data.get('count', 0)
    return jsonify({'success': True, 'water_count': data['water_count']})

@app.route('/api/habits', methods=['POST'])
def update_habits():
    """Update habits"""
    data = get_user_data()
    data['habits'].update(request.json)
    return jsonify({'success': True, 'habits': data['habits']})

@app.route('/api/meals', methods=['POST'])
def add_meal():
    """Add a meal"""
    data = get_user_data()
    new_meal = request.json
    new_meal['timestamp'] = datetime.now().strftime('%H:%M')
    
    # Remove existing meal of same type
    data['meals'] = [m for m in data['meals'] if m.get('type') != new_meal.get('type')]
    data['meals'].append(new_meal)
    
    return jsonify({'success': True, 'meals': data['meals']})

@app.route('/api/exercises', methods=['POST'])
def add_exercise():
    """Add an exercise"""
    data = get_user_data()
    new_exercise = request.json
    new_exercise['timestamp'] = datetime.now().strftime('%H:%M')
    data['exercises'].append(new_exercise)
    
    return jsonify({'success': True, 'exercises': data['exercises']})

@app.route('/api/sleep', methods=['POST'])
def add_sleep():
    """Add sleep data"""
    data = get_user_data()
    sleep_data = request.json
    
    try:
        bedtime = sleep_data['bedtime']
        wake_time = sleep_data['wake_time']
        
        bed_hour, bed_min = map(int, bedtime.split(':'))
        wake_hour, wake_min = map(int, wake_time.split(':'))
        
        bed_total = bed_hour * 60 + bed_min
        wake_total = wake_hour * 60 + wake_min
        
        if wake_total < bed_total:
            wake_total += 24 * 60
        
        duration = round((wake_total - bed_total) / 60.0, 1)
        sleep_data['duration'] = duration
        
        data['sleep_data'] = sleep_data
        
        return jsonify({'success': True, 'sleep_data': sleep_data})
    except (ValueError, KeyError):
        return jsonify({'error': 'Invalid time format'}), 400

@app.route('/api/analytics')
def get_analytics():
    """Get analytics data"""
    data = get_user_data()
    
    completed_habits = sum(1 for completed in data['habits'].values() if completed)
    total_habits = len(data['habits'])
    completion_rate = (completed_habits / total_habits * 100) if total_habits > 0 else 0
    
    total_calories_burned = sum(ex.get('calories', 0) for ex in data['exercises'])
    exercise_days = 1 if data['exercises'] else 0
    
    analytics = {
        'weekly_water': data['water_count'],
        'weekly_exercise': exercise_days,
        'habit_completion': round(completion_rate),
        'total_calories': total_calories_burned
    }
    
    return jsonify(analytics)

def main():
    """Run the application"""
    print("🌟 Starting HealthyLife Pro Web Application...")
    print("🚀 Server starting...")
    print("\n" + "="*60)
    print("🌐 HealthyLife Pro is now running!")
    print("📍 Open your browser and go to: http://localhost:5000")
    print("\n💡 Features available:")
    print("   • 💧 Water intake tracking (click the glasses!)")
    print("   • ✅ Daily habits management")
    print("   • 🍎 Nutrition logging")
    print("   • 💪 Exercise tracking") 
    print("   • 😴 Sleep monitoring")
    print("   • 📈 Real-time analytics")
    print("\n📱 The app works on desktop, tablet, and mobile!")
    print("🔄 Data automatically saves and updates in real-time")
    print("🎯 Data resets daily for fresh tracking")
    print("=" * 60 + "\n")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()


"""
🚀 QUICK START GUIDE:

1. SAVE this file as 'app.py' or 'healthylife.py'

2. INSTALL Flask:
   pip install flask

3. RUN the application:
   python app.py

4. OPEN your browser:
   Go to: http://localhost:5000

5. START TRACKING:
   ✅ Click water glasses to track hydration
   ✅ Toggle habits on/off
   ✅ Log meals and exercises
   ✅ Track sleep quality
   ✅ View real-time analytics

🎉 FEATURES:
• Beautiful responsive design
• Real-time updates
• Data persistence during session
• Mobile-friendly interface
• Interactive animations
• Comprehensive wellness tracking

🔧 TROUBLESHOOTING:
• If port 5000 is busy, Flask will suggest another port
• Make sure you have Python 3.6+ installed
• Ensure Flask is properly installed: pip install flask
• Check firewall settings if accessing from other devices

📊 The app includes:
- Water intake tracking (8 glasses daily goal)
- Customizable habit management
- Meal logging with calorie counting
- Exercise tracking with duration/calories
- Sleep monitoring with quality rating
- Analytics dashboard with progress stats

Data automatically resets each day for fresh daily tracking!
"""
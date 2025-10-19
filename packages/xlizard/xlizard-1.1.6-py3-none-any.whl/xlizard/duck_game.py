"""
Duck Game Module for xlizard
Hidden game that activates when typing 'duck'
"""

DUCK_SVG = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pgo8c3ZnIGhlaWdodD0iNjAiIHdpZHRoPSI2MCIgdmlld0JveD0iMCAwIDUxMiA1MTIiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnPgoJPHBhdGggZmlsbD0iI0QxODc3MCIgZD0iTTkwLjQ2NSwxODYuOTEyYzAuMDg2LTcuNTgxLTUuMjYtMjcuNDksMi43NzEtNDMuNzgxYzguMDI1LTE2LjI5MS00Mi4yMjYtMjAuNTQ2LTY3LjY4MiwwLjM2NwoJCWMtMjQuNTEsMjAuMTM3LDEuNzY0LDM3LjQ2OCwxNy45MzgsMzMuNjU3Qzc2LjI2NywxNjkuNDI4LDkwLjI5OSwyMDIuMjYxLDkwLjQ2NSwxODYuOTEyeiIvPgoJPHBhdGggZmlsbD0iI0REODk2OCIgZD0iTTczLjMxNSw5Ni4wMDljMC4wNzksNy41NzQtNS4yNiwyNy40ODMsMi43NjQsNDMuNzgyYzguMDI1LDE2LjI3Ny00Ni43OTksMjUuMTA1LTY3LjY3NC0wLjM3NQoJCWMtMjAuODc4LTI1LjQ4LDEuNzYtMzcuNDYxLDE3Ljk0MS0zMy42NUM1OS4xMDIsMTEzLjQ4NSw3My4xMzcsODAuNjU0LDczLjMxNSw5Ni4wMDl6Ii8+Cgk8cGF0aCBmaWxsPSIjRjZFMTc0IiBkPSJNNzYuNDUsMjY0LjIxMWMxOC4xODMtMjEuNDA2LDMzLjA5Mi0zMS4wMzgsMjAuODIxLTUwLjQzMwoJCWMtMjMuNDAyLTIzLjQwOC0zNC4zMDktNDguNzQzLTM0LjMwOS04NC40NThjMC0zNS43MDksMTQuNDc2LTY4LjAzNSwzNy44NzYtOTEuNDM2QzEyNC4yNDMsMTQuNDgzLDE1Ni41NjMsMCwxOTIuMjc4LDAKCQlzNjguMDM1LDE4LjQ4Myw5MS40NDMsMzcuODg0YzIzLjQwMSwyMy40MDIsMzcuODcsNTUuNzI4LDM3Ljg3LDkxLjQzNmMwLDUyLjc4OS00Mi4yMjIsOTUuMDExLTQyLjIyMiwxMjEuNAoJCWMtMi42NCwxMC41NjEsMTUuODM1LDIzLjc2MSwzOS41ODIsMjMuNzYxYzIzLjc2MSwwLDEwMi45MzIsMTguNDY3LDE2MC45ODgtNTguMDYzYzE1LjI4LTIxLjEyMiwzMy43NTUtOS4yMzgsMzEuNjc1LDIxLjEwNwoJCUM1MDkuNjE4LDI2Ni42MDksNDkzLjEzMyw1MTIsMzE4Ljk1MSw1MTJjLTUwLjEzNSwwLTQzLjc4OCwwLTEzOS44NzQsMGMtNDAuMDc0LDAtNzYuMzYtMTYuMjUtMTAyLjYyNy00Mi41MTMKCQljLTI2LjI3My0yNi4yNy00Mi41Mi02Mi41NTQtNDIuNTItMTAyLjY0OUMzMy45MywzMjYuNzY1LDUwLjE3NiwyOTAuNDc0LDc2LjQ1LDI2NC4yMTEiLz4KCTxwYXRoIGZpbGw9IiVFNUQyOUIiIGQ9Ik0yMTkuNTMzLDM0MC40NThoMTkzLjIxNmMyMS4xMDgsMCwyNi4zODgsMzYuOTQxLTcuOTIsNTguMDYzYzAsMjYuMzgtMTMuMjAxLDY1Ljk3LTUyLjc4Miw2NS45NwoJCWMtMzkuNTk2LDAtODcuMDkyLDAtMTIxLjQsMGMtMzQuMzE2LDAtNTguMDY0LTM5LjU5LTU4LjA2NC02My4zMzdDMTcyLjU4NCwzNzcuMzk5LDE5NS43NzcsMzQwLjQ1OCwyMTkuNTMzLDM0MC40NTh6Ii8+Cgk8cGF0aCBmaWxsPSIjRjBENzgwIiBkPSJNMjA2LjMzMSwzMjQuNjE2aDE5My4yMThjMjEuMTA4LDAsMjYuMzg4LDM2Ljk0OS03LjkyLDU4LjA2NGMwLDI2LjM5NS0xMy4xOTQsNjUuOTgzLTUyLjc3Niw2NS45ODMKCQljLTM5LjU4OSwwLTg3LjA5NywwLTEyMS40MDYsMHMtNTguMDU3LTM5LjU4OS01OC4wNTctNjMuMzQ0QzE1OS4zOSwzNjEuNTY1LDE4Mi41ODMsMzI0LjYxNiwyMDYuMzMxLDMyNC42MTZ6Ii8+Cgk8cGF0aCBmaWxsPSIjRkZGRkZGIiBkPSJNMTU5LjM5LDEwOS41MjJjMCwxNi43Ny0xMy41OTYsMzAuMzU5LTMwLjM0OCwzMC4zNTljLTE2Ljc2MywwLTMwLjM1NS0xNS41ODktMzAuMzU1LTMwLjM1OQoJCWMwLTE2Ljc0OCwxMy41OTItMzAuMzQ0LDMwLjM1NS0zMC4zNDRDMTQ1Ljc5NCw3OS4xNzcsMTU5LjM5LDkyLjc3MywxNTkuMzksMTA5LjUyMnoiLz4KCTxwYXRoIGZpbGw9IiM2NDYzNjMiIGQ9Ik0xNDMuNTU2LDEwOS41MjJjMCw4LjAyNS02LjUwMywxNC41MjUtMTQuNTE0LDE0LjUyNWMtOC4wMTgsMC0xNC41MTgtNi41LTE0LjUxOC0xNC41MjUKCQljMC04LjAwMyw2LjUtMTQuNTAzLDE0LjUxOC0xNC41MDNDMTM3LjA1Miw5NS4wMTgsMTQ3LjU1NiwxMDEuNTE4LDE0My41NTYsMTA5LjUyMnoiLz4KPC9nPgo8L3N2Zz4K"

def get_duck_game_script():
    """Returns the JavaScript code for the duck game"""
    return """
<script>
class DuckGame {
    constructor() {
        this.isActive = false;
        this.score = 0;
        this.lives = 5;
        this.ducks = [];
        this.spawnInterval = null;
        this.animationFrame = null;
        this.baseSpeed = 2;
        this.speedMultiplier = 1;
        this.gameContainer = null;
        this.scoreDisplay = null;
        this.livesDisplay = null;
        this.gameOverScreen = null;
        this.lastSpeedIncrease = 0;
        this.spawnRate = 1500;
        this.maxDucks = 7;
        this.typedChars = '';
        this.activationTimer = null;
        
        this.init();
    }

    init() {
        this.createGameUI();
        this.setupEventListeners();
    }

    createGameUI() {
        // Create game container - initially hidden
        this.gameContainer = document.createElement('div');
        this.gameContainer.id = 'duckGameContainer';
        this.gameContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10000;
            overflow: hidden;
            display: none;
        `;

        // Create score display (RIGHT TOP) - initially hidden
        this.scoreDisplay = document.createElement('div');
        this.scoreDisplay.id = 'duckGameScore';
        this.scoreDisplay.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            font-size: 24px;
            font-weight: bold;
            color: #ff6b35;
            background: rgba(255, 255, 255, 0.95);
            padding: 12px 20px;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            pointer-events: none;
            z-index: 10001;
            font-family: 'Inter', sans-serif;
            border: 3px solid rgba(255, 107, 53, 0.3);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            display: none;
            opacity: 0;
            transform: translateY(-20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        `;
        this.scoreDisplay.textContent = 'Score: 0';

        // Create lives display (LEFT TOP) - initially hidden
        this.livesDisplay = document.createElement('div');
        this.livesDisplay.id = 'duckGameLives';
        this.livesDisplay.style.cssText = `
            position: fixed;
            top: 20px;
            left: 20px;
            font-size: 24px;
            color: #ff6b35;
            background: rgba(255, 255, 255, 0.95);
            padding: 12px 20px;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            pointer-events: none;
            z-index: 10001;
            font-family: 'Inter', sans-serif;
            border: 3px solid rgba(255, 107, 53, 0.3);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            display: none;
            opacity: 0;
            transform: translateY(-20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        `;
        this.updateLivesDisplay();

        // Create game over screen
        this.gameOverScreen = document.createElement('div');
        this.gameOverScreen.id = 'duckGameOver';
        this.gameOverScreen.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(255, 255, 255, 0.98);
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
            text-align: center;
            z-index: 10002;
            pointer-events: auto;
            display: none;
            font-family: 'Inter', sans-serif;
            min-width: 350px;
            border: 4px solid rgba(255, 107, 53, 0.5);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
        `;
        this.gameOverScreen.innerHTML = `
            <h2 style="color: #ff6b35; margin-bottom: 25px; font-size: 32px;">Game Over!</h2>
            <p style="font-size: 20px; margin-bottom: 15px; color: #333;">Final Score: <span id="finalScore" style="font-weight: bold; color: #ff6b35;">0</span></p>
            <div style="display: flex; gap: 20px; justify-content: center; margin-top: 30px;">
                <button id="restartGame" style="
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 10px;
                    cursor: pointer;
                    font-size: 18px;
                    font-weight: bold;
                    box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
                    transition: all 0.3s ease;
                ">Restart</button>
                <button id="closeGame" style="
                    background: linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 10px;
                    cursor: pointer;
                    font-size: 18px;
                    font-weight: bold;
                    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
                    transition: all 0.3s ease;
                ">Work</button>
            </div>
        `;

        document.body.appendChild(this.gameContainer);
        document.body.appendChild(this.scoreDisplay);
        document.body.appendChild(this.livesDisplay);
        document.body.appendChild(this.gameOverScreen);

        // Add game over event listeners
        document.getElementById('restartGame').addEventListener('click', () => this.restartGame());
        document.getElementById('closeGame').addEventListener('click', () => this.stopGame());
        
        // Add hover effects
        const restartBtn = document.getElementById('restartGame');
        const closeBtn = document.getElementById('closeGame');
        
        restartBtn.addEventListener('mouseenter', () => {
            restartBtn.style.transform = 'translateY(-3px)';
            restartBtn.style.boxShadow = '0 6px 20px rgba(79, 172, 254, 0.6)';
        });
        restartBtn.addEventListener('mouseleave', () => {
            restartBtn.style.transform = 'translateY(0)';
            restartBtn.style.boxShadow = '0 4px 15px rgba(79, 172, 254, 0.4)';
        });
        
        closeBtn.addEventListener('mouseenter', () => {
            closeBtn.style.transform = 'translateY(-3px)';
            closeBtn.style.boxShadow = '0 6px 20px rgba(255, 107, 53, 0.6)';
        });
        closeBtn.addEventListener('mouseleave', () => {
            closeBtn.style.transform = 'translateY(0)';
            closeBtn.style.boxShadow = '0 4px 15px rgba(255, 107, 53, 0.4)';
        });
    }

    setupEventListeners() {
        // Listen for keyboard input
        document.addEventListener('keydown', (e) => {
            if (this.isActive) return;
            
            this.typedChars += e.key.toLowerCase();
            
            // Keep only last 10 characters
            if (this.typedChars.length > 10) {
                this.typedChars = this.typedChars.slice(-10);
            }
            
            // Check if "duck" is typed
            if (this.typedChars.includes('duck')) {
                if (this.activationTimer) {
                    clearTimeout(this.activationTimer);
                }
                
                this.activationTimer = setTimeout(() => {
                    if (!this.isActive) {
                        this.startGame();
                    }
                }, 300);
            }
        });

        // Listen for clicks on ducks
        this.gameContainer.addEventListener('click', (e) => {
            if (this.isActive && e.target.classList.contains('duck')) {
                this.hitDuck(e.target);
            }
        });
    }

    startGame() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.score = 0;
        this.lives = 5;
        this.ducks = [];
        this.baseSpeed = 2;
        this.speedMultiplier = 1;
        this.lastSpeedIncrease = Date.now();
        this.spawnRate = 1500;
        this.typedChars = '';
        
        this.scoreDisplay.textContent = 'Score: 0';
        this.updateLivesDisplay();
        this.gameOverScreen.style.display = 'none';
        
        this.showGameUI();
        this.startSpawning();
        this.gameLoop();
        
        console.log('🦆 Duck Game Started!');
    }

    stopGame() {
        this.isActive = false;
        this.clearGame();
        this.hideGameUI();
        console.log('🦆 Duck Game Stopped');
    }

    restartGame() {
        this.stopGame();
        setTimeout(() => this.startGame(), 100);
    }

    clearGame() {
        if (this.spawnInterval) {
            clearInterval(this.spawnInterval);
            this.spawnInterval = null;
        }
        
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }
        
        // Remove all ducks
        this.ducks.forEach(duck => {
            if (duck.element && duck.element.parentNode) {
                duck.element.remove();
            }
        });
        this.ducks = [];
    }

    hideGameUI() {
        // Hide game container
        this.gameContainer.style.display = 'none';
        
        // Hide and reset UI elements with animation
        this.scoreDisplay.style.display = 'none';
        this.scoreDisplay.style.opacity = '0';
        this.scoreDisplay.style.transform = 'translateY(-20px)';
        
        this.livesDisplay.style.display = 'none';
        this.livesDisplay.style.opacity = '0';
        this.livesDisplay.style.transform = 'translateY(-20px)';
        
        this.gameOverScreen.style.display = 'none';
    }

    showGameUI() {
        // Show game container
        this.gameContainer.style.display = 'block';
        
        // Show score and lives with smooth animation
        setTimeout(() => {
            this.scoreDisplay.style.display = 'block';
            this.livesDisplay.style.display = 'block';
            
            // Trigger animation
            setTimeout(() => {
                this.scoreDisplay.style.opacity = '1';
                this.scoreDisplay.style.transform = 'translateY(0)';
                this.livesDisplay.style.opacity = '1';
                this.livesDisplay.style.transform = 'translateY(0)';
            }, 50);
        }, 100);
    }

    startSpawning() {
        this.lastSpeedIncrease = Date.now();
        
        this.spawnInterval = setInterval(() => {
            if (this.ducks.length < this.maxDucks) {
                this.spawnDuck();
            }
        }, this.spawnRate);
    }

    spawnDuck() {
        const duck = document.createElement('div');
        duck.className = 'duck';
        duck.style.cssText = `
            position: absolute;
            width: 60px;
            height: 60px;
            background-image: url("${DUCK_SVG}");
            background-size: contain;
            background-repeat: no-repeat;
            pointer-events: auto;
            cursor: crosshair;
            top: -70px;
            left: ${Math.random() * (window.innerWidth - 80)}px;
            transition: transform 0.2s ease, opacity 0.2s ease;
            z-index: 10001;
            filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3));
        `;

        this.gameContainer.appendChild(duck);

        const duckObj = {
            element: duck,
            speed: this.baseSpeed * this.speedMultiplier,
            x: parseInt(duck.style.left),
            y: -70,
            isHit: false
        };

        this.ducks.push(duckObj);
    }

    gameLoop() {
        if (!this.isActive) return;

        const currentTime = Date.now();
        
        // Increase difficulty every 5 seconds
        if (currentTime - this.lastSpeedIncrease > 5000) {
            this.speedMultiplier = Math.min(this.speedMultiplier + 0.2, 4);
            this.spawnRate = Math.max(this.spawnRate - 100, 600);
            this.lastSpeedIncrease = currentTime;
        }

        // Update ducks
        for (let i = this.ducks.length - 1; i >= 0; i--) {
            const duck = this.ducks[i];
            if (duck.isHit) continue;

            duck.y += duck.speed;
            duck.element.style.top = duck.y + 'px';

            // Check if duck is out of bounds
            if (duck.y > window.innerHeight) {
                this.missDuck(i);
            }
        }

        this.animationFrame = requestAnimationFrame(() => this.gameLoop());
    }

    hitDuck(duckElement) {
        const duckIndex = this.ducks.findIndex(d => d.element === duckElement);
        if (duckIndex === -1 || this.ducks[duckIndex].isHit) return;

        const duck = this.ducks[duckIndex];
        duck.isHit = true;

        // Add hit effect
        duck.element.style.transform = 'scale(1.3) rotate(15deg)';
        duck.element.style.opacity = '0.5';
        duck.element.style.filter = 'brightness(2) drop-shadow(0 0 8px #ff6b35)';
        
        setTimeout(() => {
            if (duck.element && duck.element.parentNode) {
                duck.element.remove();
            }
            this.ducks.splice(duckIndex, 1);
        }, 150);

        this.score += 10;
        this.scoreDisplay.textContent = `Score: ${this.score}`;
        this.scoreDisplay.style.animation = 'none';
        setTimeout(() => {
            this.scoreDisplay.style.animation = 'scorePop 0.3s ease';
        }, 10);
    }

    missDuck(duckIndex) {
        const duck = this.ducks[duckIndex];
        if (duck.element && duck.element.parentNode) {
            duck.element.remove();
        }
        this.ducks.splice(duckIndex, 1);

        this.lives--;
        this.updateLivesDisplay();

        this.livesDisplay.style.animation = 'none';
        setTimeout(() => {
            this.livesDisplay.style.animation = 'lifeLost 0.5s ease';
        }, 10);

        if (this.lives <= 0) {
            this.gameOver();
        }
    }

    updateLivesDisplay() {
        const hearts = '❤️'.repeat(this.lives) + '♡'.repeat(5 - this.lives);
        this.livesDisplay.innerHTML = `Lives: <span style="font-size: 26px;">${hearts}</span>`;
    }

    gameOver() {
        this.isActive = false;
        this.clearGame();
        
        document.getElementById('finalScore').textContent = this.score;
        this.gameOverScreen.style.display = 'block';
    }
}

// Initialize game when page loads
let duckGame;
document.addEventListener('DOMContentLoaded', () => {
    duckGame = new DuckGame();
});

window.DuckGame = DuckGame;
</script>
"""

def get_duck_game_css():
    """Returns CSS styles for the duck game"""
    return """
<style>
.duck {
    animation: duckFloat 0.8s ease-in-out infinite alternate;
}

@keyframes duckFloat {
    0% { transform: translateY(0px) rotate(-2deg); }
    100% { transform: translateY(-8px) rotate(2deg); }
}

.duck:hover {
    filter: drop-shadow(2px 2px 6px rgba(255, 107, 53, 0.8)) brightness(1.1) !important;
    transform: scale(1.05) !important;
}

#duckGameContainer {
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
}

@keyframes scorePop {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

@keyframes lifeLost {
    0% { transform: translateX(0); }
    25% { transform: translateX(-10px); }
    50% { transform: translateX(10px); }
    75% { transform: translateX(-5px); }
    100% { transform: translateX(0); }
}

#duckGameOver {
    animation: modalAppear 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes modalAppear {
    from { 
        opacity: 0; 
        transform: translate(-50%, -50%) scale(0.7); 
    }
    to { 
        opacity: 1; 
        transform: translate(-50%, -50%) scale(1); 
    }
}

/* Responsive design */
@media (max-width: 768px) {
    #duckGameScore, #duckGameLives {
        font-size: 18px !important;
        padding: 8px 16px !important;
        top: 10px !important;
    }
    
    #duckGameLives {
        left: 10px !important;
    }
    
    #duckGameScore {
        right: 10px !important;
    }
    
    .duck {
        width: 50px !important;
        height: 50px !important;
    }
    
    #duckGameOver {
        min-width: 280px !important;
        padding: 30px !important;
    }
}
</style>
"""
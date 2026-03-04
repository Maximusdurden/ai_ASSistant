document.addEventListener('DOMContentLoaded', () => {
    const dice = document.querySelectorAll('.die');
    const rollButton = document.getElementById('roll-button');

    const rollDice = () => {
        dice.forEach(die => {
            const randomNumber = Math.floor(Math.random() * 6) + 1;
            die.textContent = randomNumber;
        });
    };

    rollButton.addEventListener('click', rollDice);

    // Initial roll when the page loads
    rollDice();
});
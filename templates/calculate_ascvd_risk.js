document.addEventListener('DOMContentLoaded', function() {

    const resultDiv = document.getElementById('result');
    const resultElement = document.getElementById('riskResult');
    const submitAnswersBtn = document.getElementById('submitAnswers');

    submitAnswersBtn.addEventListener('click', function() {
        // 從 HTML 中提取年齡
        const rows = document.querySelectorAll('tr');
        let ageElement;
        for (const row of rows) { // 使用 for...of 迴圈，更有效率且更易讀
            const cells = row.querySelectorAll('td');
            if (cells.length > 0 && cells[0].textContent.trim().includes('Age')) {
                ageElement = cells[1];
                break; // 找到後立即跳出迴圈
            }
        }
    
        let age; //宣告 age 變數
        if (ageElement) {
            const ageString = ageElement.textContent.trim();
            age = parseInt(ageString, 10);
            if (isNaN(age)) { // 處理 parseInt 失敗的情況
                handleError("Invalid age input. Please enter a valid number.");
                return;
            }
            console.log(age);
        } else {
            handleError("Could not find age element.");
            return;
        }
    
        // 檢查年齡是否在 40 - 75 之間
        if (age < 40 || age > 75) {
            resultElement.textContent = "The 10-year risk estimation requires an age range of 40 to 75.";
            resultDiv.classList.remove('hidden'); // 確保顯示錯誤區塊
            console.log(resultElement, resultDiv)
            return; // 🚫 中斷請求，避免向後端發送請求
        }

        // 檢查必填選項
        const unansweredQuestions = [];
        const questions = ['diabetes', 'smoking', 'treatingHTN'];
        for (const question of questions) {
            const checked = document.querySelector(`input[name="${question}"]:checked`);
            if (!checked) {
                document.getElementById(`${question}Error`).classList.remove('hidden');
                unansweredQuestions.push(question); // Add this line!
            } else {
                document.getElementById(`${question}Error`).classList.add('hidden');
            }
        }

        if (unansweredQuestions.length === 0) {
            // All questions answered, proceed with the calculation
            const hasDiabetes = document.querySelector('input[name="diabetes"]:checked')?.value === 'yes';
            const isSmoking = document.querySelector('input[name="smoking"]:checked')?.value === 'yes';
            const isTreatingHypertension = document.querySelector('input[name="treatingHTN"]:checked')?.value === 'yes';

            fetch('/calculate_ascvd_risk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    hasDiabetes: hasDiabetes,
                    isSmoking: isSmoking,
                    isTreatingHypertension: isTreatingHypertension
                }),
            })
            .then(response => response.json())
            .then(data => {
                resultElement.textContent = data.result;
                resultDiv.classList.remove('hidden');
            })
            .catch((error) => {
                console.error('Error:', error);
                handleError("An error occurred during the calculation. Please try again later."); // Handle fetch errors gracefully
            });
        } else {
            handleError("There are unanswered questions.");
        }
    });
});
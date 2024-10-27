// Function to handle user registration
function register() {
    const email = document.getElementById('email').value;
    const name = document.getElementById('name').value;
    const password = document.getElementById('password').value;

    if (!email || !name || !password) {
        alert('All fields are required.');
        return;
    }
    if (password.length < 6) {
        alert('Password must be at least 6 characters long.');
        return;
    }

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email, name: name, password: password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            window.location.href = '/'; 
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}

// Function to handle user login
function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const loginButton = document.getElementById('loginButton');
    const loading = document.getElementById('loading');


    loginButton.disabled = true;
    loading.style.display = 'block';


    if (!email || !password) {
        loginButton.disabled = false;
        loading.style.display = 'none';
        alert('Email and Password are required.');
        return;
    }

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'OTP sent successfully') {
            window.location.href = '/OTP'; 
        } else {
            window.location.href = '/';
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}

// Function to handle OTP verification
function verify() {
    const otp = document.getElementById('otp').value;

    if (!otp) {
        alert('Email and OTP are required.');
        return;
    }

    fetch('/verify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ otp: otp })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'OTP verified successfully') {
            window.location.href = '/main1';
        } else if (data.message === "OTP has expired. Log In again") {
            window.location.href = '/';
        } else if (data.message === "Invalid OTP") {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}

// Function to handle email confirmation
function confirmEmail() {
    const email = document.getElementById('email').value;
    const confirm = document.getElementById('confirm');
    const loading = document.getElementById('loading');

    confirm.disabled = true;
    loading.style.display = 'block';
    if (email === '') {
        confirm.disabled = false;
        loading.style.display = 'none';
        alert('Please enter your email.');
        return;
    } 

    fetch('/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Password shared to email.') {
            alert('A temporary password has been sent to your email. Please reset it to continue.')
            window.location.href = '/reset';
        } else {
            window.location.href = '/forget';
            alert('Invalid email address')
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}

function reset(){
    window.location.href = '/reset';
}

// Function to handle reset_password
function reset_password() {
    const email = document.getElementById('email').value;
    const new_password = document.getElementById('new_password').value;
    const password = document.getElementById('password').value;

    if (!email || !new_password || !password) {
        alert('All fields are required.');
        return;
    }

    if (new_password.length < 6) {
        alert('Password must be at least 6 characters long.');
        return;
    }

    fetch('/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email, new_password: new_password , password: password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.message === 'Password updated') {
            window.location.href = '/'; 
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}


function add(){
    window.location.href = '/add';
}

function generate(){
    window.location.href = '/generate';
}

function togglePasswordVisibility(index) {
    var passwordLabel = document.getElementById('password-label-' + index);
    var passwordHidden = document.getElementById('password-hidden-' + index);
    var toggleButtonIcon = document.querySelector('#password-label-' + index + ' + .password-toggle i');

    if (passwordLabel.textContent === '.............') {
        passwordLabel.textContent = passwordHidden.value;
        toggleButtonIcon.className = 'fa-regular fa-eye-slash'; 
    } else {
        passwordLabel.textContent = '.............';
        toggleButtonIcon.className = 'fa-regular fa-eye'; 
    }
}

function editEntry(site, username, password, link, notes) {
    const newsite = prompt('Enter new Title:', site)
    const newUsername = prompt('Enter new Username:', username);
    const newPassword = prompt('Enter new Password:', password);
    const newLink = prompt('Enter new Link:', link);
    const newNotes = prompt('Enter new Notes:', notes);

    if (newsite !== null && newUsername !== null && newPassword !== null) {
        fetch('/edit_entry', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                oldsite : site,
                newsite: newsite,
                username: newUsername,
                password: newPassword,
                link: newLink,
                notes: newNotes
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload(); 
            } else {
                alert('Error updating entry: ' + data.message);
            }
        });
    }
}

// Delete Entry
function deleteEntry(site) {
    if (confirm(`Are you sure you want to delete the entry for ${site}?`)) {
        fetch('/delete_entry', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                site: site
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload(); 
            } else {
                alert('Error deleting entry: ' + data.message);
            }
        });
    }
}

function copyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;  
    document.body.appendChild(textArea);  

    textArea.select(); 
    document.execCommand('copy');  
    document.body.removeChild(textArea);  
    alert('Copied to clipboard!'); 
}

function openLink(url) {
    if (url !== ''){
        window.open(url, '_blank');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const copyBtn = document.getElementById('copy-btn');
    const passwordInput = document.getElementById('password');
    const lengthInput = document.getElementById('length');
    const includeLowercase = document.getElementById('include-lowercase');
    const includeUppercase = document.getElementById('include-uppercase');
    const includeNumbers = document.getElementById('include-numbers');
    const includeSpecial = document.getElementById('include-special');

    const lowercaseChars = 'abcdefghijklmnopqrstuvwxyz';
    const uppercaseChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numberChars = '0123456789';
    const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?/';

    function generatePassword() {
        const length = parseInt(lengthInput.value);
        let characters = '';
        if (includeLowercase.checked) characters += lowercaseChars;
        if (includeUppercase.checked) characters += uppercaseChars;
        if (includeNumbers.checked) characters += numberChars;
        if (includeSpecial.checked) characters += specialChars;

        if (characters.length === 0) return '';

        let password = '';
        for (let i = 0; i < length; i++) {
            const randomIndex = Math.floor(Math.random() * characters.length);
            password += characters[randomIndex];
        }
        return password;
    }
    

    generateBtn.addEventListener('click', function() {
        const password = generatePassword();
        passwordInput.value = password;
    });

    copyBtn.addEventListener('click', function() {
        passwordInput.select();
        document.execCommand('copy');
    });
});



const otpValidityDuration = 3 * 60;
let remainingTime = otpValidityDuration;

const timerElement = document.getElementById('timer');

const updateTimer = () => {
    const minutes = Math.floor(remainingTime / 60);
    const seconds = remainingTime % 60;
    timerElement.textContent = `Time left: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

    if (remainingTime <= 0) {
        clearInterval(timerInterval);
        timerElement.textContent = 'OTP has expired. Returning to Login page';
        window.location.href = '/';
    } else {
        remainingTime--;
    }
};

const timerInterval = setInterval(updateTimer, 1000);

const errorContainer = document.querySelector('.error-container');
const name = document.querySelector('input[name="name"]');
const months = document.querySelector('select[name="months"]');
const days = document.querySelector('select[name="days"]');

name.addEventListener('focusout', function () {
    if (name.value.length < 2) {
        name.style.border = '1px solid red';
        errorContainer.style.visibility = 'visible';
    } else {
        name.style.border = '1px solid rgb(126, 126, 126)';
        errorContainer.style.visibility = 'hidden';
    }
});

/* Updates the month's days limit, and handle if the user first inputs a day (e.g. 31), and then, an invalid
month for that day (e.g. february, since February 31st it's an invalid date). */

months.addEventListener('change', function () {
    if (months.value === 'February') {
        if (days.value > 27) {
            days[28].selected = 'selected';
        }
        for (let i = 29; i < days.length; i++) {
            days[i].style.display = 'none';
        }
    } else if (
        months.value === 'April' ||
        months.value === 'June' ||
        months.value === 'September' ||
        months.value === 'November'
    ) {
        if (days.value > 29) {
            days[30].selected = 'selected';
        }
        days[29].style.display = 'block';
        days[30].style.display = 'block';
        days[31].style.display = 'none';
    } else {
        for (let i = days.length - 1; i > 28; i--) {
            days[i].style.display = 'block';
        }
    }
});

function formatTo2Digits(number) {
    return (number < 10 ? '0' : '') + number;
}

function weekDayString(weekday) {
    var weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return weekdays[weekday % 7];
}

function formatDate(date) {
    return formatTo2Digits(date.getMonth() + 1) + '/' +
        formatTo2Digits(date.getDate()) + '/' +
        formatTo2Digits(date.getFullYear())  + ' ' +
        formatTo2Digits(date.getHours())  + ':' +
        formatTo2Digits(date.getMinutes())  + ':' +
        formatTo2Digits(date.getSeconds());
}

var Utils = {
    formatTo2Digits: formatTo2Digits,
    weekDayString: weekDayString,
    formatDate: formatDate,
};

window.Utils = Utils;

if (module && module.exports) {
    module.exports = Utils;
}


/* global bootstrap */

// Auto dismiss alert msg after 5 seconds
document.addEventListener('DOMContentLoaded',function() {
    setTimeout(function() {
        let alerts =document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });}, 5000);
});

// To confirm before cancelling booking
function cancelConfirm() {
    return confirm('Do you want to cancel the booking?');
}

// Setting the minimum date today to book 
document.addEventListener('DOMContentLoaded', function() {
    let startTime = document.getElementById('id_start_time');
    let endTime= document.getElementById('id_end_time');
    if (startTime) {
        let now =new Date().toISOString().slice(0,16);
        startTime.min =now;
        endTime.min =now;
    }
});


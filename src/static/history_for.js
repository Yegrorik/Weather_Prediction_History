function assembleTime() {
    const hourFrom = document.getElementById('hour_from').value;
    const minuteFrom = document.getElementById('minute_from').value;
    const secondFrom = document.getElementById('second_from').value;
    
    let timeFromValue = '';
    if (hourFrom || minuteFrom || secondFrom) {
        const h = hourFrom || '00';
        const m = minuteFrom || '00';
        const s = secondFrom || '00';
        timeFromValue = `${h.padStart(2, '0')}:${m.padStart(2, '0')}:${s.padStart(2, '0')}`;
    }
    document.getElementById('time_from').value = timeFromValue;
    
    const hourTo = document.getElementById('hour_to').value;
    const minuteTo = document.getElementById('minute_to').value;
    const secondTo = document.getElementById('second_to').value;
    
    let timeToValue = '';
    if (hourTo || minuteTo || secondTo) {
        const h = hourTo || '00';
        const m = minuteTo || '00';
        const s = secondTo || '00';
        timeToValue = `${h.padStart(2, '0')}:${m.padStart(2, '0')}:${s.padStart(2, '0')}`;
    }
    document.getElementById('time_to').value = timeToValue;
    
    console.log('Assembled time:', { 
        timeFrom: timeFromValue || 'not specified', 
        timeTo: timeToValue || 'not specified' 
    });
    
    return { timeFrom: timeFromValue, timeTo: timeToValue };
}

function validateDateTime() {
    const dateFrom = document.getElementById('date_from').value;
    const dateTo = document.getElementById('date_to').value;
    const { timeFrom, timeTo } = assembleTime();
    
    console.log('Validation:', { dateFrom, dateTo, timeFrom, timeTo });
    
    if (dateFrom && dateTo) {
        if (dateFrom > dateTo) {
            alert('❌ "From" date cannot be later than "To" date');
            return false;
        }
        
        if (dateFrom === dateTo && timeFrom && timeTo) {
            if (timeFrom > timeTo) {
                alert('❌ "From" time cannot be later than "To" time on the same date');
                return false;
            }
        }
    }
    
    return true;
}

function validateAndSubmit() {
    assembleTime();
    
    if (!validateDateTime()) {
        return false;
    }
    
    return true;
}

function restoreTimeFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    
    const timeFrom = urlParams.get('time_from');
    if (timeFrom) {
        const [hours, minutes, seconds] = timeFrom.split(':');
        document.getElementById('hour_from').value = hours || '';
        document.getElementById('minute_from').value = minutes || '';
        document.getElementById('second_from').value = seconds || '';
        document.getElementById('time_from').value = timeFrom;
    }
    
    const timeTo = urlParams.get('time_to');
    if (timeTo) {
        const [hours, minutes, seconds] = timeTo.split(':');
        document.getElementById('hour_to').value = hours || '';
        document.getElementById('minute_to').value = minutes || '';
        document.getElementById('second_to').value = seconds || '';
        document.getElementById('time_to').value = timeTo;
    }
    
    console.log('Restored from URL:', { timeFrom, timeTo });
}

function setDateTimeRange(rangeType) {
    const now = new Date();
    
    switch(rangeType) {
        case 'today':
            setDateTimeValues(now, now);
            break;
            
        case 'yesterday':
            const yesterday = new Date(now);
            yesterday.setDate(now.getDate() - 1);
            setDateTimeValues(yesterday, yesterday);
            break;
            
        case 'week':
            const weekAgo = new Date(now);
            weekAgo.setDate(now.getDate() - 7);
            setDateTimeValues(weekAgo, now);
            break;
            
        case 'month':
            const monthAgo = new Date(now);
            monthAgo.setDate(now.getDate() - 30);
            setDateTimeValues(monthAgo, now);
            break;
            
        case 'current_hour':
            const hourStart = new Date(now);
            hourStart.setMinutes(0, 0, 0);
            const hourEnd = new Date(now);
            hourEnd.setMinutes(59, 59, 999);
            setDateTimeValues(hourStart, hourEnd);
            break;
    }
    
    highlightActiveDateTimeFilters();
    
    setTimeout(() => {
        if (validateAndSubmit()) {
            document.getElementById('weatherForm').submit();
        }
    }, 300);
}

function setDateTimeValues(fromDate, toDate) {
    document.getElementById('date_from').value = formatDate(fromDate);
    document.getElementById('date_to').value = formatDate(toDate);
    
    document.getElementById('hour_from').value = formatTimeComponent(fromDate.getHours());
    document.getElementById('minute_from').value = formatTimeComponent(fromDate.getMinutes());
    document.getElementById('second_from').value = formatTimeComponent(fromDate.getSeconds());
    
    document.getElementById('hour_to').value = formatTimeComponent(toDate.getHours());
    document.getElementById('minute_to').value = formatTimeComponent(toDate.getMinutes());
    document.getElementById('second_to').value = formatTimeComponent(toDate.getSeconds());
    
    assembleTime();
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function formatTimeComponent(component) {
    return component.toString().padStart(2, '0');
}

function clearDateTime() {
    document.getElementById('hour_from').value = '';
    document.getElementById('minute_from').value = '';
    document.getElementById('second_from').value = '';
    document.getElementById('hour_to').value = '';
    document.getElementById('minute_to').value = '';
    document.getElementById('second_to').value = '';
    
    document.getElementById('time_from').value = '';
    document.getElementById('time_to').value = '';
    
    highlightActiveDateTimeFilters();
}

function highlightActiveDateTimeFilters() {
    const dateFrom = document.getElementById('date_from');
    const dateTo = document.getElementById('date_to');
    
    dateFrom.classList.toggle('datetime-active', !!dateFrom.value);
    dateTo.classList.toggle('datetime-active', !!dateTo.value);
    
    const timeFromActive = document.getElementById('hour_from').value || 
                        document.getElementById('minute_from').value || 
                        document.getElementById('second_from').value;
    
    const timeToActive = document.getElementById('hour_to').value || 
                        document.getElementById('minute_to').value || 
                        document.getElementById('second_to').value;
    
    const timeControls = document.querySelectorAll('.time-controls');
    if (timeControls[0]) timeControls[0].classList.toggle('time-active', !!timeFromActive);
    if (timeControls[1]) timeControls[1].classList.toggle('time-active', !!timeToActive);
}

document.querySelectorAll('.date-input, .time-select').forEach(element => {
    element.addEventListener('change', function() {
        assembleTime();
        highlightActiveDateTimeFilters();
    });
});

function resetAllFilters() {
    window.location.href = "/";
}

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('city');
    if (searchInput) {
        searchInput.focus();
    }
    
    restoreTimeFromUrl();
    
    highlightActiveDateTimeFilters();
    
    assembleTime();
});

const cacheBadges = document.querySelectorAll('.cache-badge');
cacheBadges.forEach(badge => {
    badge.title = "This request was loaded from cache";
});
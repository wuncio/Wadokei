let hours = 0;
let minutes = 0;
let seconds = 0;
let secInMinute = 0;
let day = 0;
let night = 0;
let deg_s = 0;
let deg_e = 0;
let q_s = 0;
let q_e = 0;
let hourAngle = 0;
let minuteAngle = 0;
let hourDelta = 0;
let minuteDelta = 0;
let refreshRate = 0.05; //The interval of time on which the clock refreshes, in seconds

function map(value, in_min, in_max, out_min, out_max, mod = null) {
    let range;
    let offset;
    if(mod != null){
      range = (in_max >= in_min) ? in_max - in_min : (in_max - in_min) + mod;
      offset = (value - in_min + mod) % mod;
    }
    else{
      range = in_max - in_min;
      offset = value - in_min;
    }
    return offset / range * (out_max - out_min) + out_min;
}

function updateClock() {
    hourAngle += hourDelta;
    minuteAngle += minuteDelta;
    seconds = (seconds + refreshRate) % secInMinute;
    document.getElementById("hourHand").style.transform = `translateX(-50%) rotate(${hourAngle}deg)`;
    document.getElementById("minuteHand").style.transform = `translateX(-50%) rotate(${minuteAngle}deg)`;
    document.getElementById("secondsDisplay").textContent = `Seconds: ${Math.floor(seconds).toString().padStart(2, '0')}`;
}

function formatTime(date) {
    return date.toLocaleTimeString('en-GB', {hour12: false});
}

function describeSector(cx, cy, radius, startAngle, endAngle) {
    const rad = Math.PI / 180;
    const x1 = cx + radius * Math.cos(rad * startAngle);
    const y1 = cy + radius * Math.sin(rad * startAngle);
    const x2 = cx + radius * Math.cos(rad * endAngle);
    const y2 = cy + radius * Math.sin(rad * endAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? 0 : 1;

    return [
      `M ${cx} ${cy}`,
      `L ${x1} ${y1}`,
      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
      'Z'
    ].join(' ');
}

function setShadedSector(startHour, angleSize = 90) {
    const startAngle = ((startHour % 12) * 30) - 90; // shift so 0h = top
    const endAngle = startAngle + angleSize;

    const path = describeSector(50, 50, 50, startAngle, endAngle); // center: 50, radius: 48
    document.getElementById("shadePath").setAttribute("d", path);
}

function updateTimeDisplays() {
    const now = new Date();
    document.getElementById("localTime").textContent = `Local: ${formatTime(now)}`;

    const nyTime = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));
    const londonTime = new Date(now.toLocaleString("en-US", { timeZone: "Europe/London" }));
    const tokyoTime = new Date(now.toLocaleString("en-US", { timeZone: "Asia/Tokyo" }));
    const sydneyTime = new Date(now.toLocaleString("en-US", { timeZone: "Australia/Sydney" }));

    document.getElementById("nyTime").textContent = `New York: ${formatTime(nyTime)}`;
    document.getElementById("londonTime").textContent = `London: ${formatTime(londonTime)}`;
    document.getElementById("tokyoTime").textContent = `Tokyo: ${formatTime(tokyoTime)}`;
    document.getElementById("sydneyTime").textContent = `Sydney: ${formatTime(sydneyTime)}`;
}

function setTimezone() {
    const selectedZone = document.getElementById("timezoneSelect").value;
    return fetch('/set_timezone', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ timezone: selectedZone })
    })
    .then(response => response.json())
    .then(data => {
      console.log("Timezone updated:", data.time_zone);
    })
    .catch(error => {
      console.error('Error updating timezone:', error);
    });
}


function getTimezoneInfo(){
    return fetch('/get_timezone_info')
    .then(response => response.json())
    .then(data => {
        hours = Math.floor(data.hours);
        minutes = Math.floor(data.minutes);
        seconds = Math.floor(data.seconds);
        day = data.len_day;
        night = data.len_night;
        deg_s = data.deg_start;
        deg_e = data.deg_end;
        q_s = data.qt_start;
        q_e = data.qt_end;

        secInMinute = Math.round(((((q_e - q_s) % 24) + 24) % 24) / 12 * 60);

        let periodLen = (q_e >= q_s) ? q_e - q_s : (q_e - q_s) + 24;
        let periodDeg = Math.abs(deg_s - deg_e);


        hourAngle = map(hours + minutes / 60, q_s, q_e, deg_s, deg_e, 24) - 90;
        timePassed = map(hours + minutes / 60, q_s, q_e, 0, 1, 24);
        minuteAngle = map(timePassed * 12 % 1, 0, 1, 0, 360);

        hourDelta = map(refreshRate / 3600, 0, periodLen, 0, periodDeg);
        minuteDelta = map(refreshRate / secInMinute, 0, 60, 0, 360) ;

        console.log("Hour delta: " + hourDelta);
        console.log("Minute delta: " + minuteDelta);
        console.log("Start hour: " + q_s);
        console.log("End hour: " + q_e);
        console.log(hours.toString() +":"+ minutes.toString() +":"+ seconds.toString());
        console.log("Hour starting angle: " + hourAngle);
        console.log("Length of minute: " + secInMinute);
        console.log("Lenght of period: " + periodLen);
        console.log("Share of period passed: " + timePassed);
        console.log("Wadokei hors passed: " + timePassed*12);
    });
}
// Obracanie clockinner.png

let innerAngle = 0;
let anglePerSecond = 0;

function rotateClockInner(angle) {
  const inner = document.getElementById("clockInner");
  if (inner) {
    inner.style.transform = `rotate(${angle}deg)`;
  }
}

function startClockRotation() {
  fetch('/check_date')
    .then(response => response.json())
    .then(data => {
      innerAngle = data.angle;
      const D = data.days;

      // Oblicz kąt obrotu na sekundę
      anglePerSecond = 30 / (D * 24 * 60 * 60);

      // Rozpocznij obracanie co sekundę
      setInterval(() => {
        innerAngle = (innerAngle + anglePerSecond) % 360;
        rotateClockInner(innerAngle);
      }, 1000);
      console.log("Rotation angle: " + innerAngle);
    })
    .catch(error => {
      console.error("Błąd podczas pobierania danych:", error);
    });
}


function addCustomTimezone() {
    const input = document.getElementById("customTimezoneField");
    const select = document.getElementById("timezoneSelect");
    const customValue = input.value.trim();

    if (customValue && ![...select.options].some(opt => opt.value === customValue)) {
        document.getElementById("customTimezoneField").value = "";
        const option = document.createElement("option");
        option.value = customValue;
        option.textContent = customValue;
        select.appendChild(option);
        select.value = customValue;
        handleTimezoneChange();
    }
    // dodane
    let savedTimezones = JSON.parse(localStorage.getItem("recentTimezones")) || [];
    // usuń jeśli jest, żeby nie duplikować
    savedTimezones = savedTimezones.filter(tz => tz !== customValue);
    // dodaj na początek
    savedTimezones.unshift(customValue);
    // ogranicz do 5
    savedTimezones = savedTimezones.slice(0, 5);
    // zapisz z powrotem
    localStorage.setItem("recentTimezones", JSON.stringify(savedTimezones));

    // ustaw wybraną wartość i zapisz ostatnio wybraną
    select.value = customValue;
    localStorage.setItem("selectedTimezone", customValue);

    handleTimezoneChange();
    // dodane
}


    // Your function here
async function handleTimezoneChange() {
    // Zapisz wybraną strefę czasową do localStorage
    const selectedTimezone = document.getElementById("timezoneSelect").value;
    localStorage.setItem("selectedTimezone", selectedTimezone);

    document.getElementById("clockApp").classList.add("hidden");
    document.getElementById("loadingScreen").classList.remove("hidden");

    await setTimezone();
    getTimezoneInfo();
    startClockRotation();

    document.getElementById("loadingScreen").classList.add("hidden");
    document.getElementById("clockApp").classList.remove("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
    const savedTimezone = localStorage.getItem("selectedTimezone");
    const select = document.getElementById("timezoneSelect");

    if (savedTimezone && select) {
        select.value = savedTimezone;
        handleTimezoneChange();
    }
    // dodane
    const savedTimezones = JSON.parse(localStorage.getItem("recentTimezones")) || [];
    savedTimezones.forEach(tz => {
        if (![...select.options].some(opt => opt.value === tz)) {
            const option = document.createElement("option");
            option.value = tz;
            option.textContent = tz;
            select.appendChild(option);
        }
    });

    if (savedTimezones.length > 0) {
        select.value = savedTimezones[0];
        if (input) input.value = savedTimezones[0];
        handleTimezoneChange();
    }else {
        select.value = savedTimezone;
        if (input) {
            input.value = savedTimezone;
        }
        handleTimezoneChange();
    }
    // dodane
});

/* Make async HTTP requests. */
function xdr(url, callback, errback) {
    var req;

    if(XMLHttpRequest) {
        req = new XMLHttpRequest();
        if('withCredentials' in req) {
            req.open('GET', url, true);
            req.onerror = errback;
            req.onreadystatechange = function() {
                if (req.readyState === 4) {
                    if (req.status >= 200 && req.status < 400) {
                        callback(JSON.parse(req.response));
                    } else {
                        errback();
                    }
                }
            };
            req.send();
        }
    } else if(XDomainRequest) {
        req = new XDomainRequest();
        req.open('GET', url);
        req.onerror = errback;
        req.onload = function() {
            callback(JSON.parse(data));
        };
        req.send();
    } else {
        errback();
    }
}


function populateUsers(payload) {
    var board = document.getElementById('table-scores');
    board.innerHTML = null;

    var currentUser = document.getElementById('username').innerText.trim();
    var currentScores = document.createElement('tbody');
    currentScores.id = "table-scores";

    for (var i = 0; i < payload.users.length; i++) {
        var row = currentScores.insertRow(i);

        var pos = row.insertCell(0);
        var player = row.insertCell(1);
        var level = row.insertCell(2);

        pos.innerHTML = (i + 1);
        player.innerHTML = payload.users[i].name;

        if (payload.users[i].name == currentUser) {
            row.className = "current-user";
        }

        level.innerHTML = payload.users[i].level;
    }

    board.parentNode.replaceChild(currentScores, board);
}

function populateError(message) {
    console.log('Unable to fetch leaderboard data.');
    var board = document.getElementById('track');
    board.innerHTML = null;
}

/* Make a request once. */
xdr('/tracker', populateUsers, populateError);

/* Run it every minute. */
setInterval(function() {
    xdr('/tracker', populateUsers, populateError)
}, 60000);

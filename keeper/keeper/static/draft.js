 $(document).ready(function() {
            function createDraftTable() {
                var body = document.body, tbl = document.createElement('table');
                tbl.style.border = '1px solid black';

                for (var i = 0; i < 25; i++) {
                    var tr = tbl.insertRow();
                    for (var j = 0; j < 11; j++) {
                        var td = tr.insertCell();
                        td.style.border = '1px solid black'
                        if (i == 0 || j == 0) {
                            var bold = document.createElement("B");
                            if (j != 0) { // Header
                                td.id = 'team' + j;
                                bold.appendChild(document.createTextNode('Team ' + j));
                            } else if (i != 0) { // First Column
                                bold.appendChild(document.createTextNode('Round ' + i));
                            }
                            td.appendChild(bold);
                        } else { // Data cells
                            td.id = j + (10 * (i-1));
                        }
                    }
                }
                body.appendChild(tbl);
            }

            createDraftTable();

            // Connect to the Socket.IO server.
            // The connection URL has the following format:
            //     http[s]://<domain>:<port>[/<namespace>]
            var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

            socket.on('draft_player', function(msg) {
                $('#' + msg.pick).text(msg.player.data);
                $('#draft_data').val('');
            });

            socket.on('update_board', function(picks) {
                for (var pick in picks) {
                    $('#' + pick).text(picks[pick]);
                }
            });

            $('form#draft').submit(function(event) {
                socket.emit('draft_event', {data: $('#draft_data').val()});
                return false;
            });
        });
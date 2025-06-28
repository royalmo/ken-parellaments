function makeEditableSpan(text, onRename) {
    const span = document.createElement('span');
    span.classList.add('editable-span')
    span.textContent = text;
    span.onclick = () => {
        const input = document.createElement('input');
        input.type = 'text';
        input.value = span.textContent;
        input.onblur = () => {
            const oldValue = span.textContent;
            const newValue = input.value.trim();
            if (newValue && newValue !== oldValue) {
                span.textContent = newValue;
                onRename(oldValue, newValue);
            } else {
                span.textContent = oldValue;
            }
            span.onclick = () => makeEditableSpan(newValue, onRename);
        };
        span.replaceWith(input);
        input.focus();
    };
    return span;
}

function renderTeamList(listId, items) {
    const ul = document.getElementById(listId);
    ul.innerHTML = '';
    items.forEach(item => {
        const li = document.createElement('li');
        const span = makeEditableSpan(item, (oldName, newName) => renameEverywhere('team', oldName, newName));
        li.appendChild(span);
        const delBtn = document.createElement('button');
        delBtn.textContent = '×';
        delBtn.className = 'btn btn-sm btn-danger ms-2';
        delBtn.onclick = () => {
            if (confirm("S'eliminarà l'equip de la llista d'exclusions (si hi és).\n\nContinuar?")) {
                li.remove(); teamRemoved(item);
            }
        };
        li.appendChild(delBtn);
        ul.appendChild(li);
    });
}

function renderSportsList(listId, items, numDays) {
    const ul = document.getElementById(listId);
    ul.innerHTML = '';
    items.forEach(item => {
        const li = document.createElement('li');
        const span1 = makeEditableSpan(item[0], (oldName, newName) => renameEverywhere('sport', oldName, newName));
        li.appendChild(span1);

        const span = document.createElement('span');
        span.style.display = 'flex';
        span.style.flexGrow = '0';

        const daysDiv = document.createElement('div');
        daysDiv.classList.add('days-div');
        span.appendChild(daysDiv);
        renderDaysDiv(daysDiv);
        item[1].forEach((day) => {
            if (day <= numDays)
                toggleDayCheck(daysDiv.querySelector(`.day-${day}`));
        })

        const delBtn = document.createElement('button');
        delBtn.textContent = '×';
        delBtn.className = 'btn btn-sm btn-danger ms-2';
        delBtn.onclick = () => {
            if (confirm("S'eliminarà l'esport de la llista d'obligatoris (si hi és).\n\nContinuar?")) {
                li.remove(); sportRemoved(item[0]);
            }
        };
        span.appendChild(delBtn);

        li.appendChild(span);
        ul.appendChild(li);
    });
}

function renameEverywhere(type, oldVal, newVal) {
    if (type === 'team') {
        document.querySelectorAll('#excludeTeam1 option, #excludeTeam2 option').forEach(opt => {
            if (opt.value === oldVal) opt.textContent = opt.value = newVal;
        });
        document.querySelectorAll('#exclusionList li').forEach(li => {
            let [a, b] = li.dataset.pair.split(',');
            if (a === oldVal) a = newVal;
            if (b === oldVal) b = newVal;
            li.dataset.pair = `${a},${b}`;
            li.childNodes[0].nodeValue = `${a},${b}`;
        });
    } else if (type === 'sport') {
        document.querySelectorAll('.must-have-group select').forEach(select => {
            select.querySelectorAll('option').forEach(opt => {
                if (opt.value === oldVal) opt.value = opt.textContent = newVal;
            });
        });
    }
}

function teamRemoved(team) {
    document.getElementById('exclusionList').childNodes.forEach((ch) => {
        if(ch.dataset.pair.split(',').indexOf(team) !== -1) {
            ch.remove();
        }
    });
    updateTeamSelectors();
}

function sportRemoved(sport) {
    document.getElementById('mustHaveContainer').childNodes.forEach((ch) => {
        ch.querySelector('.sport-selects').childNodes.forEach((chch) => {
            if(chch.querySelector('select>option:checked').value == sport) {
                chch.remove();
            }
        });
    });
    updateSportSelectors();
}

function updateTeamSelectors() {
    const teams = [...document.getElementById('teamList').children].map(li => li.querySelector('span.editable-span').textContent.trim());
    const selects = [document.getElementById('excludeTeam1'), document.getElementById('excludeTeam2')];
    selects.forEach(select => {
        select.innerHTML = '';
        teams.forEach(team => {
        const opt = document.createElement('option');
        opt.value = team;
        opt.textContent = team;
        select.appendChild(opt);
        });
    });
}

function updateSportSelectors() {
    const sports = [...document.getElementById('sportList').children].map(li => li.querySelector('span.editable-span').textContent.trim());
    document.querySelectorAll('.must-have-group').forEach(group => {
        const container = group.querySelector('.sport-selects');
        container.childNodes.forEach((select) => {
            const currentSport = select.querySelector('select>option:checked').value;
            select.outerHTML = '';
            addSportSelect(container, sports, currentSport);
        })
    });
}

function addSportSelect(container, sports, selectedSport) {
    const div = document.createElement('div');
    div.className = 'input-group mb-1';
    const select = document.createElement('select');
    select.className = 'form-select';
    sports.forEach(sport => {
        const opt = document.createElement('option');
        opt.value = sport;
        opt.textContent = sport;
        if (opt.value == selectedSport) opt.selected = true;
        select.appendChild(opt);
    });
    const delBtn = document.createElement('button');
    delBtn.className = 'btn btn-outline-danger';
    delBtn.type = 'button';
    delBtn.textContent = '×';
    delBtn.onclick = () => div.remove();
    div.appendChild(select);
    div.appendChild(delBtn);
    container.appendChild(div);
}

function addMustHaveGroup(add_first_select=true) {
    const sports = [...document.getElementById('sportList').children].map(li => li.querySelector('span.editable-span').textContent.trim());
    const group = document.createElement('div');
    group.className = 'must-have-group border rounded p-2 mb-2';
    const container = document.createElement('div');
    container.className = 'sport-selects';
    group.appendChild(container);
    const addBtn = document.createElement('button');
    addBtn.className = 'btn btn-sm btn-secondary';
    addBtn.type = 'button';
    addBtn.textContent = 'Afegir esport';
    addBtn.onclick = () => addSportSelect(container, sports);
    group.appendChild(addBtn);
    document.getElementById('mustHaveContainer').appendChild(group);
    if (add_first_select) addSportSelect(container, sports);
    else return [container, sports];
}

function renderDaysDiv(daysDiv) {
    daysDiv.innerHTML = '<small>Dies: </small>';
    numDays = document.getElementById('numDaysInput').value;

    for (let i=1; i<=numDays; i++) {
        const dayBtn = document.createElement('button');
        dayBtn.className = `btn btn-sm me-1 btn-secondary day-btn day-${i}`;
        dayBtn.type = 'button';
        dayBtn.textContent = `${i}`;
        dayBtn.onclick = () => toggleDayCheck(dayBtn);
        daysDiv.appendChild(dayBtn);
    }
}

function toggleDayCheck(dayBtn) {
    if (dayBtn.classList.contains('checked')) {
        dayBtn.classList.remove('checked');
        dayBtn.classList.remove('btn-primary');
        dayBtn.classList.add('btn-secondary');
    }
    else {
        dayBtn.classList.add('checked');
        dayBtn.classList.remove('btn-secondary');
        dayBtn.classList.add('btn-primary');
    }
}

function addItem(type) {
    const input = document.getElementById(type + 'Input');
    const value = input.value.replaceAll(',', '').trim();
    if (!value) return;
    const ul = document.getElementById(type + 'List');
    const li = document.createElement('li');
    li.textContent = value;

    const span = document.createElement('span');
    span.style.display = 'flex';

    if (type=='sport') {
        const daysDiv = document.createElement('div');
        daysDiv.classList.add('days-div');
        span.appendChild(daysDiv);
        renderDaysDiv(daysDiv);
    }

    const delBtn = document.createElement('button');
    delBtn.textContent = '×';
    delBtn.className = 'btn btn-sm btn-danger ms-2';
    delBtn.onclick = () => {
        if (type=='sport') {
            if (confirm("S'eliminarà l'esport de la llista d'obligatoris (si hi és).\n\nContinuar?")) {
                li.remove(); sportRemoved(value);
            }
        }
        else {
            if (confirm("S'eliminarà l'equip de la llista d'exclusions (si hi és).\n\nContinuar?")) {
                li.remove(); teamRemoved(item);
            }
        }
    };
    span.appendChild(delBtn);

    li.appendChild(span);
    ul.appendChild(li);
    input.value = '';
    if (type === 'team') updateTeamSelectors();
    if (type === 'sport') updateSportSelectors();
}

function addExclusion(t1, t2) {
    if (!t1) t1 = document.getElementById('excludeTeam1').value;
    if (!t2) t2 = document.getElementById('excludeTeam2').value;
    if (!t1 || !t2 || t1 === t2) return;
    const ul = document.getElementById('exclusionList');
    const pair = `${t1},${t2}`;
    for (const li of ul.children) {
        if (li.dataset.pair === pair || li.dataset.pair === `${t2},${t1}`) return;
    }
    const li = document.createElement('li');
    li.dataset.pair = pair;
    li.textContent = pair;
    const delBtn = document.createElement('button');
    delBtn.textContent = '×';
    delBtn.className = 'btn btn-sm btn-danger';
    delBtn.onclick = () => li.remove();
    li.appendChild(delBtn);
    ul.appendChild(li);
}

function getLiContent(li) {
    const span = li.querySelector('span.editable-span');
    if (span) return span.textContent.trim();
    const input = li.querySelector('input');
    return input ? input.value.trim() : '';
}

function handleSubmit() {
    document.getElementById('teamsHidden').value = [...document.getElementById('teamList').children]
        .map(li => getLiContent(li))
        .join('\n');
    document.getElementById('sportsHidden').value = [...document.getElementById('sportList').children]
        .map(li => `${getLiContent(li)},${[...li.querySelectorAll('.day-btn.checked')].map(e => e.textContent.trim()).join(',')}`)
        .join('\n');
    document.getElementById('exclusionsHidden').value = [...document.getElementById('exclusionList').children]
        .map(li => li.dataset.pair)
        .join('\n');
    document.getElementById('musthavesHidden').value = [...document.querySelectorAll('.must-have-group')]
        .map(group => [...group.querySelectorAll('select')].map(s => s.value).join(',')).join('\n');
    return true;
}

async function loadJSON(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load ${url}: ${response.statusText}`);
    }
    return await response.json();
}

function initPairings(jsonData) {
    document.getElementById('numDaysInput').value = jsonData.num_days;
    document.getElementById('numRoundsInput').value = jsonData.num_rounds;
    document.getElementById('startHourInput').value = jsonData.start_time_hour;
    document.getElementById('startMinInput').value = jsonData.start_time_min;
    document.getElementById('startDayInput').value = jsonData.start_day;

    renderTeamList('teamList', jsonData.teams);
    renderSportsList('sportList', jsonData.sports, jsonData.num_days);
    Sortable.create(document.getElementById('teamList'), { animation: 150 });
    Sortable.create(document.getElementById('sportList'), { animation: 150 });
    updateTeamSelectors();
    updateSportSelectors();

    jsonData.exclusions.forEach((i) => {addExclusion(i[0], i[1])});
    jsonData.musts.forEach((row) => {
        output = addMustHaveGroup(false);
        row.forEach((sport) => {
            addSportSelect(output[0], output[1], sport);
        });
    });

    document.getElementById('numDaysInput').onchange = function () {
        Array.from(document.getElementsByClassName('days-div')).forEach((e) => renderDaysDiv(e));
    }
}

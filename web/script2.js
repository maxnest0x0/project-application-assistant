let data;
try {
    data = JSON.parse(sessionStorage.application);
} catch {
    window.location.href = '/';
}

document.querySelector('#title').value = data.title;
document.querySelector('#description').value = data.description;
document.querySelector('#goal').value = data.goal;
document.querySelector('#result').value = data.result;
document.querySelector('#criteria').value = data.criteria.join('\n');
document.querySelector('#max_participants').value = +data.max_participants;

function downloadJSON() {
    const blob = new Blob([JSON.stringify(data, null, 2)]);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'project.json';
    a.click();
    URL.revokeObjectURL(url);
}

function downloadExcel() {
    const aoa = [
        ['Название', data.title],
        ['Описание', data.description],
        ['Цель', data.goal],
        ['Результат', data.result],
        ['Критерии', ...data.criteria],
        ['Образовательная программа', data.educational_program],
        ['Количество участников', data.max_participants],
    ];
    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.aoa_to_sheet(aoa);
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Проект');
    XLSX.writeFile(workbook, 'project.xlsx');
}

document.querySelector('#json-btn').addEventListener('click', downloadJSON);
document.querySelector('#excel-btn').addEventListener('click', downloadExcel);

var table = document.getElementById('todos');
var button_save = document.getElementById('form-button');
var task_id_field = document.getElementById('task-id');
var edit_form = document.getElementById('todo-form');
var button_delete = document.getElementById('form-button-delete');
var boolString = 'true';

function ChangeDateFormat(date_string) {
    var date = Date.parse(date_string);
    return Intl.DateTimeFormat('de-DE').format(date);
}

function ResetForm() {
    task_id_field.value = "";
    edit_form.task.value =  "";
    edit_form.priority.value =  "";
    edit_form.due_date.value =  "";
    edit_form.completed.value = "false"
}

function ToDoEdit(row_no) {
    task_id_field.value = table.rows[row_no].cells[0].innerHTML;
    edit_form.task.value =  table.rows[row_no].cells[1].innerHTML;
    edit_form.priority.value =  table.rows[row_no].cells[2].innerHTML;
    edit_form.due_date.value =  table.rows[row_no].cells[3].getAttribute('date');
    edit_form.completed.value = ((table.rows[row_no].cells[4].innerHTML == 'Yes') ? true : false);
    
    button_save.innerHTML = 'Save'
    button_save.setAttribute('onclick', `ToDoSave(${table.rows[row_no].cells[0].innerHTML})`)
    ToggleHideDeleteButton()
    button_delete.setAttribute('onclick', `ToDoDelete(${table.rows[row_no].cells[0].innerHTML})`)

}

function ToggleHideDeleteButton() {
    var hidden = button_delete.getAttribute('hidden')

    if (hidden) {
        button_delete.removeAttribute("hidden")
    } else {
        button_delete.setAttribute("hidden", "hidden")
    }
}

async function ToDoGetAll() {
    const response = await fetch("/api/v1/todos/");
    const todos = await response.json();
    
    var today = new Date()

    table.innerHTML = "";

    for (var i = 0; i < todos.length; i++) {
        var row = table.insertRow(i);
         
        // Create cells
        var todo_id = row.insertCell(0);
        var todo_task = row.insertCell(1);
        var todo_priority = row.insertCell(2);
        var todo_due_date = row.insertCell(3);
        var todo_completed = row.insertCell(4);
        var todo_edit = row.insertCell(5);

        // Set values
        todo_id.outerHTML = `<th scope="row">${todos[i]['id']}</th>`;
        todo_task.innerHTML = todos[i]['task'];
        todo_priority.innerHTML = todos[i]['priority'];
        todo_due_date.setAttribute('date', todos[i]['due_date'])
        todo_due_date.innerHTML = ChangeDateFormat(todos[i]['due_date']);
        todo_completed.innerHTML = ((todos[i]['completed'] == true) ? 'Yes' : 'No');
        todo_edit.innerHTML = '<img src="static/img/pencil.svg">';
        
        // Change style
        todo_priority.style = 'text-align: center';
        todo_due_date.style = 'text-align: center';
        todo_completed.style = 'text-align: center';
        todo_edit.style = 'text-align: center';
        
        if (todos[i]['completed'] == true) {
            row.classList.add("table-success")
        } else if (Date.parse(todos[i]['due_date']) < today.setHours(0, 0, 0, 0)) {
            row.classList.add("table-warning")
        };

        // Onclick events
        todo_edit.setAttribute('onclick', `ToDoEdit(${i});`)
        
        if ((todos[i]['completed'] == false)) {
            todo_completed.setAttribute('ondblclick', `ToDoCompleted(${todos[i]['id']});`)
        }
    }
}

async function ToDoAdd() {
    var todo_form = new FormData(document.getElementById('todo-form'));
    todo_new = {};
    todo_form.forEach((value, key) => todo_new[key] = value);
    
    const response = await fetch("/api/v1/todos/", {
        method: "POST",
        body: JSON.stringify(todo_new)
    });
    // const todos = await response.json();
    
    ToDoGetAll();
}

async function ToDoCompleted(id) {
    todo_change = {'completed': true}
    
    const response = await fetch("/api/v1/todos/"+id, {
        method: "PUT",
        body: JSON.stringify(todo_change)
    });
    const todos = await response.json();
    
    ToDoGetAll()
}

async function ToDoSave() {
    var todo_form = new FormData(document.getElementById('todo-form'));
    var task_id = document.getElementById('task-id').value;

    todo_new = {};
    todo_form.forEach((value, key) => todo_new[key] = value);
    
    console.log(todo_new['completed'])

    if ((todo_new['completed'] === boolString)) {
        todo_new['completed'] = true;
    } else {
        todo_new['completed'] = false;
    };
    
    const response = await fetch(`/api/v1/todos/${task_id}`, {
        method: "PUT",
        body: JSON.stringify(todo_new)
    });
        
    button_save.innerHTML = 'Add';
    button_save.setAttribute('onclick', 'ToDoAdd()');
    
    ToggleHideDeleteButton();
    ResetForm();
    ToDoGetAll();
}

async function ToDoDelete() {
    var task_id = document.getElementById('task-id').value;
    
    const response = await fetch(`/api/v1/todos/${task_id}`, {
        method: "DELETE"       
    });
        
    button_save.innerHTML = 'Add';
    button_save.setAttribute('onclick', 'ToDoAdd()');
    
    ToggleHideDeleteButton();
    ResetForm();
    ToDoGetAll();
}

ToDoGetAll()
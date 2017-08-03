// Dialog confirmation message used when an admin deletes logs

function delete_log(id) {
    BootstrapDialog.confirm({
        title: 'Delete log entry?',
        message: 'Are you sure you wish to delete log ' + id + '?',
        type: BootstrapDialog.TYPE_DANGER,
        btnOKLabel: 'Confirm',
        callback: function(result){
            if(result)
                window.location.assign(window.location.href + '/delete/' + id);
        }
    });
}

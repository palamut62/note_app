$(document).ready(function() {
    // CSRF token'ı almak için yardımcı fonksiyon
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // AJAX ayarları
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });

    // Kategori işlemleri
    $('#addCategory').click(function() {
        $('#categoryModal').modal('show');
    });

    $('#categoryForm').submit(function(e) {
        e.preventDefault();
        $.post("/add_category/", $(this).serialize(), function(data) {
            if (data.id) {
                $('#categoryList').append(`
                    <li class="category-item d-flex justify-content-between align-items-center mb-2">
                        ${data.name}
                        <div>
                            <i class="fas fa-edit edit-category" data-id="${data.id}"></i>
                            <i class="fas fa-trash delete-category" data-id="${data.id}"></i>
                        </div>
                    </li>
                `);
                $('#categoryModal').modal('hide');
                $('#categoryForm')[0].reset();
            }
        }).fail(function(xhr) {
            alert('Kategori eklenirken bir hata oluştu: ' + xhr.responseJSON.error);
        });
    });

    // Not işlemleri
    $('#newNote').click(function() {
        window.location.href = "/create_note/";
    });

    // Edit note
    $(document).on('click', '.edit-note', function() {
        let noteId = $(this).data('id');
        window.location.href = `/edit_note/${noteId}/`;
    });

    // Delete note
    $(document).on('click', '.delete-note', function() {
        let noteId = $(this).data('id');
        $('#deleteConfirmModal').modal('show');
        $('#confirmDelete').data('id', noteId);
        $('#confirmDelete').data('type', 'note');
    });

    // Edit category
    $(document).on('click', '.edit-category', function() {
        let categoryId = $(this).data('id');
        let categoryName = $(this).closest('.category-item').find('span').text();
        $('#categoryModal h5.modal-title').text('Kategori Düzenle');
        $('#categoryForm input[name="name"]').val(categoryName);
        $('#categoryForm').data('id', categoryId);
        $('#categoryModal').modal('show');
    });

    // Delete category
    $(document).on('click', '.delete-category', function() {
        let categoryId = $(this).data('id');
        $('#deleteConfirmModal').modal('show');
        $('#confirmDelete').data('id', categoryId);
        $('#confirmDelete').data('type', 'category');
    });

    // Confirm delete
    $('#confirmDelete').click(function() {
        let id = $(this).data('id');
        let type = $(this).data('type');
        let url = type === 'note' ? `/delete_note/${id}/` : `/delete_category/${id}/`;

        $.ajax({
            url: url,
            type: 'POST',
            success: function(data) {
                if (data.success) {
                    $(`[data-id="${id}"]`).closest(type === 'note' ? '.note' : '.category-item').remove();
                    $('#deleteConfirmModal').modal('hide');
                } else {
                    alert('Silme işlemi başarısız oldu.');
                }
            },
            error: function() {
                alert('Bir hata oluştu. Lütfen tekrar deneyin.');
            }
        });
    });

    // Tag filtreleme
    $('.tag').click(function() {
        let tagId = $(this).data('id');
        $.get(`/filter_notes_by_tag/${tagId}/`, function(data) {
            $('.notes-grid').empty();
            data.notes.forEach(function(note) {
                $('.notes-grid').append(`
                    <div class="note" style="background-color: ${note.color || '#ffd700'};">
                        <h3>${note.title}</h3>
                        <p>${note.content.length > 100 ? note.content.substring(0, 100) + '...' : note.content}</p>
                        <div class="note-footer">
                            <small>${new Date(note.created_at).toLocaleDateString()}</small>
                            <div class="note-actions">
                                <i class="fas fa-edit edit-note" data-id="${note.id}"></i>
                                <i class="fas fa-trash delete-note" data-id="${note.id}"></i>
                            </div>
                        </div>
                    </div>
                `);
            });
        });
    });

    // Tüm Kategoriler butonu
    $('#allCategories').click(function() {
        window.location.reload();
    });

    // Upcoming tasks için checkbox işlevi
    $('.upcoming-task input[type="checkbox"]').change(function() {
        let taskId = $(this).attr('id').split('-')[1];
        $.post(`/complete_task/${taskId}/`, {
            completed: this.checked
        }, function(data) {
            if (data.success) {
                // Görev tamamlandığında yapılacak işlemler (örn. görevin stilini değiştirme)
            }
        });
    });

    // Renk seçici için
    $('input[type="color"]').on('change', function() {
        $(this).closest('.note').css('background-color', $(this).val());
    });

    // Hatırlatıcı ekleme/düzenleme için
    $('input[type="datetime-local"]').on('change', function() {
        let noteId = $(this).closest('.note').data('id');
        let reminderTime = $(this).val();
        $.post(`/set_reminder/${noteId}/`, {
            reminder: reminderTime
        }, function(data) {
            if (data.success) {
                // Hatırlatıcı ikonunu güncelleme
                if (reminderTime) {
                    $(this).closest('.note').find('.reminder-icon').show();
                } else {
                    $(this).closest('.note').find('.reminder-icon').hide();
                }
            }
        });
    });
});


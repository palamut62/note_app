$(document).ready(function () {
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


    // Kategori ekleme
    $('#categoryForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: "/categories/add/",
            type: "POST",
            data: $(this).serialize(),
            success: function (data) {
                if (data.id) {
                    $('#categoryList').append(`
                        <li class="category-item d-flex justify-content-between align-items-center mb-2" data-id="${data.id}">
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
            },
            error: function (xhr) {
                alert('Kategori eklenirken bir hata oluştu: ' + xhr.responseJSON.error);
            }
        });
    });

    // Not işlemleri
    $('#newNote').click(function () {
        window.location.href = "/create/";
    });

    // Edit note
    $(document).on('click', '.edit-note', function () {
        let noteId = $(this).data('id');
        window.location.href = `/notes/edit/${noteId}/`;
    });

    // Delete note
    $(document).on('click', '.delete-note', function () {
        let noteId = $(this).data('id');
        $('#deleteConfirmModal').modal('show');
        $('#confirmDelete').data('id', noteId);
        $('#confirmDelete').data('type', 'note');
    });

    // Edit category
    $(document).on('click', '.edit-category', function () {
        let categoryId = $(this).data('id');
        let categoryName = $(this).closest('.category-item').text().trim();
        $('#categoryModal h5.modal-title').text('Kategori Düzenle');
        $('#categoryForm input[name="name"]').val(categoryName);
        $('#categoryForm').data('id', categoryId);
        $('#categoryModal').modal('show');
    });

    // Delete category
    $(document).on('click', '.delete-category', function () {
        let categoryId = $(this).data('id');
        $('#deleteConfirmModal').modal('show');
        $('#confirmDelete').data('id', categoryId);
        $('#confirmDelete').data('type', 'category');
    });

    // Confirm delete
    $('#confirmDelete').click(function () {
        let id = $(this).data('id');
        let type = $(this).data('type');
        let url = type === 'note' ? `/notes/delete/${id}/` : `/categories/delete/${id}/`;

        $.ajax({
            url: url,
            type: 'POST',
            success: function (data) {
                if (data.success) {
                    $(`[data-id="${id}"]`).closest(type === 'note' ? '.note' : '.category-item').remove();
                    $('#deleteConfirmModal').modal('hide');
                } else {
                    alert('Silme işlemi başarısız oldu: ' + data.error);
                }
            },
            error: function (xhr) {
                alert('Bir hata oluştu. Lütfen tekrar deneyin.');
            }
        });
    });

    // Etiket filtreleme
    $(document).on('click', '.clickable-tag', function () {
        var tagId = $(this).data('id');
        var url = tagId === 'all' ? '/all-notes/' : '/filter-by-tag/' + tagId + '/';

        $.ajax({
            url: url,
            type: 'GET',
            success: function (response) {
                $('.notes-grid').empty();

                if (response.notes && response.notes.length > 0) {
                    response.notes.forEach(function (note) {
                        var noteHtml = `
                            <div class="note-wrapper">
                                <div class="note" style="background-color: ${note.color || '#2a2a3a'};" data-id="${note.id}">
                                    <div class="note-header">
                                        ${note.is_active && note.reminder ?
                            `<i class="fas fa-bell alarm-icon" title="Hatırlatıcı: ${new Date(note.reminder).toLocaleString()}"></i>` :
                            '<span></span>'}
                                        <div class="category-badge">${note.category}</div>
                                    </div>
                                    <h3 class="note-title">${note.title}</h3>
                                    <p class="note-content">${note.content}</p>
                                    <div class="note-footer">
                                        <small>${new Date(note.created_at).toLocaleDateString()}</small>
                                        <div class="note-actions">
                                            <i class="fas fa-edit edit-note" data-id="${note.id}"></i>
                                            <i class="fas fa-trash delete-note" data-id="${note.id}"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                        $('.notes-grid').append(noteHtml);
                    });
                } else {
                    $('.notes-grid').append('<p>Not bulunamadı.</p>');
                }
            },
            error: function (xhr, status, error) {
                console.error('Notlar yüklenirken bir hata oluştu:', status, error);
            }
        });
    });

    // Kategori filtreleme
    $(document).on('click', '.clickable-category', function (e) {
        // Eğer tıklanan öğe edit veya delete ikonu değilse kategori filtreleme işlemini yap
        if (!$(e.target).hasClass('edit-category') && !$(e.target).hasClass('delete-category')) {
            var categoryId = $(this).data('id');
            var url = categoryId === 'all' ? '/all-notes/' : '/filter-by-category/' + categoryId + '/';

            $.ajax({
                url: url,
                type: 'GET',
                success: function (response) {
                    $('.notes-grid').empty();

                    if (response.notes && response.notes.length > 0) {
                        response.notes.forEach(function (note) {
                            var noteHtml = `
                                <div class="note-wrapper">
                                    <div class="note" style="background-color: ${note.color || '#2a2a3a'};" data-id="${note.id}">
                                        <div class="note-header">
                                            ${note.is_active && note.reminder ?
                                `<i class="fas fa-bell alarm-icon" title="Hatırlatıcı: ${new Date(note.reminder).toLocaleString()}"></i>` :
                                '<span></span>'}
                                            <div class="category-badge">${note.category}</div>
                                        </div>
                                        <h3 class="note-title">${note.title}</h3>
                                        <p class="note-content">${note.content}</p>
                                        <div class="note-footer">
                                            <small>${new Date(note.created_at).toLocaleDateString()}</small>
                                            <div class="note-actions">
                                                <i class="fas fa-edit edit-note" data-id="${note.id}"></i>
                                                <i class="fas fa-trash delete-note" data-id="${note.id}"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;
                            $('.notes-grid').append(noteHtml);
                        });
                    } else {
                        $('.notes-grid').append('<p>Not bulunamadı.</p>');
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Notlar yüklenirken bir hata oluştu:', status, error);
                }
            });
        }
    });

    $(document).on('click', '.view-note-details', function () {
        var noteId = $(this).data('id');
        $.ajax({
            url: '/note-details/' + noteId + '/',
            type: 'GET',
            success: function (response) {
                $('#noteTitle').text(response.title);
                $('#noteContent').text(response.content);
                $('#noteCategory').text(response.category || 'Kategorisiz');
                $('#noteTags').text(response.tags.join(', ') || 'Etiket yok');
                $('#noteCreatedAt').text(new Date(response.created_at).toLocaleString());
                $('#noteUpdatedAt').text(new Date(response.updated_at).toLocaleString());

                if (response.reminder) {
                    $('#noteReminderContainer').show();
                    $('#noteReminder').text(new Date(response.reminder).toLocaleString());
                } else {
                    $('#noteReminderContainer').hide();
                }

                $('#noteStatus').text(response.is_active ? 'Aktif' : 'Pasif');

                $('#noteDetailModal').modal('show');
            },
            error: function (xhr, status, error) {
                console.error('Not detayları yüklenirken bir hata oluştu:', status, error);
            }
        });
    });
// Tüm Kategoriler butonu
    $('#allCategories').click(function () {
        window.location.reload();
    });

    // Profil resmi güncelleme
    $('#profileImageForm').submit(function (e) {
        e.preventDefault();
        var formData = new FormData(this);

        $.ajax({
            url: '/update-profile-image/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    $('#profile-picture-preview').attr('src', response.image_url);
                    $('#updateProfileImageModal').modal('hide');
                } else {
                    alert('Bir hata oluştu: ' + response.error);
                }
            },
            error: function () {
                alert('Bir hata oluştu. Lütfen tekrar deneyin.');
            }
        });
    });

    function checkReminders() {
        console.log("checkReminders fonksiyonu çağrıldı.");
        $.ajax({
            url: '/check-reminders/',
            type: 'GET',
            success: function (response) {
                console.log("AJAX çağrısı başarılı. Yanıt:", response);
                if (response.reminders && response.reminders.length > 0) {
                    var message = "Hatırlatıcılar: " + response.reminders.map(r => r.title).join(', ');
                    console.log("Oluşturulan mesaj:", message);
                    $('#reminderMessage').text(message);
                    $('#reminderAlert').fadeIn().delay(10000).fadeOut();
                    console.log("reminderAlert gösterildi.");

                    // Deaktif olan notların alarm ikonlarını kaldır
                    response.reminders.forEach(function (reminder) {
                        $(`.note[data-id="${reminder.id}"] .alarm-icon`).remove();
                        console.log(`Alarm ikonu kaldırıldı: ${reminder.id}`);
                    });

                    // Aktif hatırlatıcılar listesinden kaldır
                    response.reminders.forEach(function (reminder) {
                        $(`#activeReminders li[data-id="${reminder.id}"]`).remove();
                        console.log(`Hatırlatıcı kaldırıldı: ${reminder.id}`);
                    });

                    // Eğer liste boşsa, "Aktif hatırlatıcı yok" mesajını göster
                    if ($('#activeReminders li').length === 0) {
                        $('#activeReminders').html('<li>Aktif hatırlatıcı yok</li>');
                        console.log("Aktif hatırlatıcı kalmadı mesajı eklendi.");
                    }
                }
            },
            error: function (xhr, status, error) {
                console.error('Hatırlatıcılar kontrol edilirken bir hata oluştu:', status, error);
                console.log('XHR yanıtı:', xhr.responseText);
            }
        });
    }

});

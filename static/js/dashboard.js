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

    // Tag filtreleme
    $('.tag').click(function () {
        let tagId = $(this).data('id');
        $.get(`/filter-by-tag/${tagId}/`, function (data) {
            $('.notes-grid').empty();
            data.notes.forEach(function (note) {
                $('.notes-grid').append(`
                    <div class="note" style="background-color: ${note.color || '#ffd700'};" data-id="${note.id}">
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
});
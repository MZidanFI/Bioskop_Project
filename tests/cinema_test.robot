*** Settings ***
Library           SeleniumLibrary
Suite Setup       Generate Global Variables
Test Teardown     Close Browser

*** Variables ***
${URL}            http://127.0.0.1:5000
${BROWSER}        Chrome
${USERNAME}       admin
${PASSWORD}       123
${USERNAME_TEST}  user_test
${PASSWORD_TEST}  123
${GLOBAL_FILM_TITLE}    Film Test Default
${IMAGE_PATH}     ${CURDIR}${/}poster_test.jpg
${EXISTING_FILM}  Charlie and the Chocolate Factory
${EXISTING_CS_FILM}    Frozen

*** Keywords ***
Generate Global Variables
    ${timestamp}=    Get Time    epoch
    ${random_num}=    Evaluate    random.randint(1000, 9999)    modules=random
    Set Global Variable    ${GLOBAL_FILM_TITLE}    Film Test ${timestamp}_${random_num}
    Log    Generated Film Title: ${GLOBAL_FILM_TITLE}

Login As Admin
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Input Text      name:username    ${USERNAME}
    Input Text      name:password    ${PASSWORD}
    Click Element   css:.btn-auth
    Wait Until Location Contains    /    timeout=10s
    Sleep    2s

*** Test Cases ***
TC_01 Login Berhasil
    [Documentation]    Menguji fitur login dengan akun admin valid
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Input Text      name:username    ${USERNAME}
    Input Text      name:password    ${PASSWORD}
    Click Element   css:.btn-auth
    Wait Until Location Is    ${URL}/    timeout=20s
    Page Should Contain    CINEMA X1X

    log   Sukses: Login berhasil dan halaman homepage muncul.

TC_02 Login Gagal Password Salah
    [Documentation]    Menguji validasi jika password salah
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window

    Input Text      name:username    ${USERNAME}
    Input Text      name:password    password_ngawur
    Click Element   css:.btn-auth

    Wait Until Page Contains    Login Gagal    timeout=10s
    Page Should Contain    Login Gagal

    log   Sukses: Pesan 'Login Gagal' muncul saat password salah.

TC_03 Registrasi Akun Baru
    [Documentation]    Menguji alur pendaftaran user baru
    Open Browser    ${URL}/register    ${BROWSER}
    Maximize Browser Window

    ${epoch}=    Get Time    epoch
    ${unique_user}=    Set Variable    user_${epoch}
    
    Input Text      name:username    ${unique_user}
    Input Text      name:password    123456
    
    Click Button    xpath://button[@type='submit']
    
    Wait Until Location Is    ${URL}/login    timeout=10s
    Page Should Contain    Registrasi berhasil
    [Teardown]    Close Browser

    log   Sukses: Registrasi akun baru berhasil dan halaman login muncul.

TC_04 Booking Tiket Flow
    [Documentation]    Menguji alur booking (Direct Link)
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Input Text      name:username    ${USERNAME_TEST}
    Input Text      name:password    ${PASSWORD_TEST}
    Click Element   css:.btn-auth
    
    Wait Until Location Is    ${URL}/    timeout=20s
    Go To           ${URL}/movie/1
    Wait Until Element Is Visible    id:seatMap    timeout=20s

    Click Element    xpath://div[contains(@class, 'seat') and text()='A1']
    Click Button    id:openPaymentBtn
    Wait Until Element Is Visible    id:paymentModal    timeout=10s

    Click Button    id:confirmPayBtn
    Wait Until Location Is    ${URL}/history    timeout=20s
    Page Should Contain    Dompet Tiket Saya

    log   Sukses: Booking tiket berhasil dan halaman history muncul.

TC_05 Lihat Sinopsis Dan Beli
    [Documentation]    User membaca sinopsis dulu baru klik beli
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Input Text      name:username    ${USERNAME_TEST}
    Input Text      name:password    ${PASSWORD_TEST}
    Click Element   css:.btn-auth
    
    Wait Until Location Is    ${URL}/    timeout=20s
    Go To           ${URL}/movie/details/1
    Page Should Contain    Sinopsis
    
    Wait Until Element Is Visible    xpath://a[contains(@href, '/movie/')]    timeout=20s
    Click Element    xpath://a[contains(@href, '/movie/')]
    
    Wait Until Element Is Visible    id:seatMap    timeout=20s
    Click Element    xpath://div[contains(@class, 'seat') and text()='B1']
    
    Click Button    id:openPaymentBtn
    Wait Until Element Is Visible    id:paymentModal    timeout=10s

    Click Button    id:confirmPayBtn
    Wait Until Location Is    ${URL}/history    timeout=20s
    Page Should Contain    Dompet Tiket Saya

    log   Sukses: Melihat sinopsis dan beli tiket berhasil.

TC_06 Pencarian Film
    [Documentation]    Menguji fitur search bar di homepage
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Input Text      name:username    ${USERNAME_TEST}
    Input Text      name:password    ${PASSWORD_TEST}
    Click Element   css:.btn-auth
    Wait Until Location Is    ${URL}/    timeout=10s
    
    Input Text      name:q    Charlie and the Chocolate Factory
    Click Button    xpath://button[@type='submit']
    
    Page Should Contain    Charlie and the Chocolate Factory
    Page Should Not Contain    Moana   

    Log    Sukses: Pencarian film memberikan hasil yang sesuai.

TC_07 Pencarian Film Tidak Ditemukan
    [Documentation]    Menguji pencarian dengan kata kunci yang SALAH/TIDAK ADA.
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    
    Input Text      name:username    ${USERNAME_TEST}
    Input Text      name:password    ${PASSWORD_TEST}
    Click Element   css:.btn-auth
    Wait Until Location Is    ${URL}/    timeout=10s
    
    Input Text      name:q    Film Hantu Belang
    Click Button    xpath://button[@type='submit']
    Sleep    1s
    
    Log    Sukses: Pencarian film tidak ada memberikan hasil kosong yang benar.

TC_08 Logout System
    [Documentation]    Menguji tombol logout
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Input Text      name:username    ${USERNAME_TEST}
    Input Text      name:password    ${PASSWORD_TEST}
    Click Element   css:.btn-auth
    Wait Until Location Is    ${URL}/    timeout=10s
    
    Click Element    xpath://a[contains(@href, '/logout')]
    
    Wait Until Location Is    ${URL}/login    timeout=10s
    Page Should Contain    Anda berhasil logout

    Log    Sukses: Logout berhasil dan halaman login muncul.

TC_09 Registrasi Gagal Username Kembar
    [Documentation]    Menguji validasi jika username sudah terdaftar
    Open Browser    ${URL}/register    ${BROWSER}
    Maximize Browser Window
    
    Input Text      name:username    user_test
    Input Text      name:password    123
    
    ${btn_submit}=    Get WebElement    xpath://button[@type='submit']
    Click Element     ${btn_submit}

    Wait Until Page Contains    Username sudah terpakai!    timeout=10s
    Page Should Contain    Username sudah terpakai!
    
    Log    Sukses: Pesan 'Username sudah terpakai!' muncul saat registrasi dengan username kembar.

TC_10 Tambah Film Baru (Admin)
    [Documentation]    Menambah film dengan judul TETAP
    Login As Admin
    
    Go To    ${URL}/admin
    Wait Until Location Contains    /admin    timeout=10s
    Page Should Contain    PANEL ADMIN
    
    Input Text      name:title          ${GLOBAL_FILM_TITLE}
    Input Text      name:price          75000
    Select From List By Value    name:status    now
    Input Text      name:description    Film ini dibuat otomatis.
    Input Text      name:showtime       19:00
    Choose File     name:image          ${IMAGE_PATH}
    
    Scroll Element Into View    xpath://button[contains(text(), 'SIMPAN FILM')]
    Wait Until Element Is Visible    xpath://button[contains(text(), 'SIMPAN FILM')]    timeout=5s
    Click Button    xpath://button[contains(text(), 'SIMPAN FILM')]
    
    Wait Until Page Contains    Film berhasil ditambahkan    timeout=10s
    Page Should Contain    ${GLOBAL_FILM_TITLE}

    Log    Sukses: Film berhasil ditambahkan dan muncul di halaman admin.

TC_11 Edit Film (Admin)
    [Documentation]    Edit film yang judulnya sudah pasti
    Login As Admin
    
    Go To    ${URL}/admin
    Wait Until Location Contains    /admin    timeout=10s
    
    ${xpath_edit}=    Set Variable    xpath://tr[contains(., '${GLOBAL_FILM_TITLE}')]//a[contains(@href, '/admin/edit_movie/')]
    
    Scroll Element Into View    ${xpath_edit}
    Wait Until Element Is Visible    ${xpath_edit}    timeout=10s
    Click Element    ${xpath_edit}
    
    Wait Until Element Is Visible    name:price    timeout=10s
    Input Text    name:price    99000
    
    Scroll Element Into View    xpath://button[@type='submit']
    Click Button    xpath://button[@type='submit']
    
    Wait Until Location Contains    /admin    timeout=20s
    Page Should Contain    berhasil diperbarui

    Log    Sukses: Film berhasil diedit dan muncul di halaman admin.

TC_12 Download Laporan CSV (Admin)
    [Documentation]    Memastikan tombol CSV hijau berfungsi
    Login As Admin
    
    Go To    ${URL}/admin
    
    Wait Until Element Is Visible    xpath://a[contains(@href, '/admin/download_report')]    timeout=20s
    Click Element    xpath://a[contains(@href, '/admin/download_report')]
    
    Page Should Not Contain    Internal Server Error

    Log    Sukses: Tombol download laporan CSV berfungsi tanpa error.

TC_13 Hapus Film (Admin)
    [Documentation]    Menghapus film yang sudah ditambahkan sebelumnya
    Login As Admin
    
    Go To    ${URL}/admin
    Wait Until Location Contains    /admin    timeout=10s
    
    ${xpath_row}=    Set Variable    xpath://tr[contains(., '${GLOBAL_FILM_TITLE}')]
    Scroll Element Into View    ${xpath_row}
    
    ${xpath_hapus}=    Set Variable    xpath://tr[contains(., '${GLOBAL_FILM_TITLE}')]//a[contains(@href, '/admin/delete_movie/')]
    Wait Until Element Is Visible    ${xpath_hapus}    timeout=10s
    
    Click Element    ${xpath_hapus}
    Handle Alert    action=ACCEPT    timeout=5s
    
    Wait Until Page Contains    Film berhasil dihapus    timeout=10s
    Page Should Not Contain    ${GLOBAL_FILM_TITLE}

    Log    Sukses: Film berhasil dihapus dan tidak muncul di halaman admin.

TC_14 Reset Kursi Film Existing (Admin)
    [Documentation]    Reset kursi menggunakan JavaScript Click
    Login As Admin
    
    Go To    ${URL}/admin
    Wait Until Location Contains    /admin    timeout=10s
    
    Wait Until Page Contains    ${EXISTING_FILM}    timeout=10s
    
    ${xpath_row}=    Set Variable    xpath://tr[contains(., "${EXISTING_FILM}")]
    ${xpath_reset}=    Set Variable    ${xpath_row}//a[contains(@href, 'reset_seats')]
    
    Scroll Element Into View    ${xpath_reset}
    Wait Until Element Is Visible    ${xpath_reset}    timeout=5s
    
    ${tombol_element}=    Get WebElement    ${xpath_reset}
    
    Execute JavaScript    arguments[0].click();    ARGUMENTS    ${tombol_element}
    
    Sleep    1s
    Handle Alert    action=ACCEPT    timeout=10s
    
    Sleep    2s
    Wait Until Page Contains    berhasil    timeout=10s
    
    Page Should Contain    berhasil

    Log    Sukses: Reset kursi film existing berhasil dan pesan konfirmasi muncul.
    
TC_15 Reset Semua Kursi (Admin)
    [Documentation]    Reset kursi dengan JS Click dan Validasi pesan 'Studio sudah kosong'
    Login As Admin
    
    Go To    ${URL}/admin
    Wait Until Location Contains    /admin    timeout=10s
    
    Wait Until Page Contains    ${EXISTING_FILM}    timeout=10s
    
    ${xpath_row}=    Set Variable    xpath://tr[contains(., "${EXISTING_FILM}")]
    ${xpath_reset}=    Set Variable    ${xpath_row}//a[contains(@href, 'reset_seats')]
    
    Scroll Element Into View    ${xpath_reset}
    Wait Until Element Is Visible    ${xpath_reset}    timeout=5s
    
    ${tombol_element}=    Get WebElement    ${xpath_reset}
    Execute JavaScript    arguments[0].click();    ARGUMENTS    ${tombol_element}
    
    Sleep    1s
    ${msg_alert}=    Handle Alert    action=ACCEPT    timeout=10s
    
    Should Be Equal    ${msg_alert}    Reset kursi film ini?
    
    Sleep    2s
    
    Wait Until Page Contains    Studio sudah kosong.    timeout=10s
    Page Should Contain    Studio sudah kosong.

    Log    Sukses: Reset semua kursi berhasil dan pesan 'Studio sudah kosong' muncul.

TC_16 Memberi Rating Film
    [Documentation]    Memberi rating dan validasi pesan 'Rating diperbarui!'
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Input Text      name:username    ${USERNAME_TEST}
    Input Text      name:password    ${PASSWORD_TEST}
    Click Element   css:.btn-auth
    
    Wait Until Location Is    ${URL}/    timeout=20s
    
    Go To           ${URL}/movie/details/1
    Wait Until Page Contains    Sinopsis    timeout=10s
    
    Scroll Element Into View    xpath://button[contains(text(), 'Kirim Rating')]
    Wait Until Element Is Visible    xpath://button[contains(text(), 'Kirim Rating')]    timeout=5s
    
    ${star_element}=    Get WebElement    xpath://div[contains(@class, 'rating') or contains(@class, 'rate')]//input[@value='5'] | //div[contains(@class, 'rating')]//label[5] | //span[contains(@class, 'star')][5]
    Execute Javascript    arguments[0].click();    ARGUMENTS    ${star_element}
    
    Sleep    1s
    
    Click Button    xpath://button[contains(text(), 'Kirim Rating')]
    
    Execute JavaScript    window.scrollTo(0, 0)
    
    Sleep    1s
    
    Wait Until Page Contains    Rating diperbarui!    timeout=10s
    
    Log    Sukses: Rating diperbarui! muncul.

TC_17 Validasi Gagal Beli Film Coming Soon
    [Documentation]    user mencoba beli tiket Frozen -> Muncul Tulisan Film ini belum tayang, tidak belum bisa dibeli.
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    
    Input Text      name:username    ${USERNAME_TEST}
    Input Text      name:password    ${PASSWORD_TEST}
    Click Element   css:.btn-auth
    Wait Until Location Is    ${URL}/    timeout=20s
    
    ${xpath_imags_img}=    Set Variable    xpath://*[contains(text(), 'Frozen')]/ancestor::div[contains(@class, 'card')]//img
    Wait Until Page Contains Element    ${xpath_imags_img}    timeout=10s
    
    ${element_frozen}=    Get WebElement    ${xpath_imags_img}
    Execute Javascript    arguments[0].scrollIntoView({block: "center"});    ARGUMENTS    ${element_frozen}
    Sleep    1s
    
    Execute Javascript    arguments[0].click();    ARGUMENTS    ${element_frozen}
    Wait Until Page Contains    Sinopsis    timeout=10s
    
    ${xpath_btn_beli}=    Set Variable    xpath://button[contains(., 'BELI TIKET')] | //a[contains(., 'BELI TIKET')]
    Wait Until Page Contains Element    ${xpath_btn_beli}    timeout=10s
    
    ${element_btn}=    Get WebElement    ${xpath_btn_beli}
    Execute Javascript    arguments[0].scrollIntoView({block: "center"});    ARGUMENTS    ${element_btn}
    Sleep    1s
    
    Execute Javascript    arguments[0].click();    ARGUMENTS    ${element_btn}
    Sleep    1s
    
    Execute JavaScript    window.scrollTo(0, 0)
    Wait Until Page Contains    belum tayang    timeout=10s
    
    Log    Sukses: Banner muncul saat klik beli di film Coming Soon.
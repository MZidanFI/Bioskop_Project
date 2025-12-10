document.addEventListener('DOMContentLoaded', function() {
    // ambil data dari variabel global (yang dikirim dari HTML)
    if (typeof bookingConfig === 'undefined') {
        console.error("Error: bookingConfig tidak ditemukan. Pastikan script config ada di HTML.");
        return;
    }

    const price = bookingConfig.price;
    const bookedSeats = bookingConfig.bookedSeats;
    const movieId = bookingConfig.movieId;

    // definisi elemen DOM
    const rows = ['A', 'B', 'C', 'D', 'E'];
    const cols = 6;
    const seatMap = document.getElementById('seatMap');
    const openPaymentBtn = document.getElementById('openPaymentBtn');
    const confirmPayBtn = document.getElementById('confirmPayBtn');
    const totalPriceEl = document.getElementById('total-price');
    const modalTotalPriceEl = document.getElementById('modal-total-price');
    const loadingOverlay = document.getElementById('loadingOverlay');

    let selectedSeats = [];

    // generate kursi (grid system)
    rows.forEach(row => {
        for (let i = 1; i <= cols; i++) {
            const seatId = row + i;
            const seatDiv = document.createElement('div');
            seatDiv.classList.add('seat');
            seatDiv.innerText = seatId;
            
            if (bookedSeats.includes(seatId)) {
                seatDiv.classList.add('occupied');
            } else {
                seatDiv.addEventListener('click', () => {
                    if (seatDiv.classList.contains('selected')) {
                        seatDiv.classList.remove('selected');
                        selectedSeats = selectedSeats.filter(s => s !== seatId);
                    } else {
                        seatDiv.classList.add('selected');
                        selectedSeats.push(seatId);
                    }
                    updateInfo();
                });
            }
            seatMap.appendChild(seatDiv);
        }
    });

    // update info harga & status tombol
    function updateInfo() {
        const currentTotal = selectedSeats.length * price;
        
        if(totalPriceEl) totalPriceEl.innerText = currentTotal.toLocaleString();
        if(modalTotalPriceEl) modalTotalPriceEl.innerText = currentTotal.toLocaleString();
        
        if (selectedSeats.length > 0) {
            openPaymentBtn.removeAttribute('disabled');
        } else {
            openPaymentBtn.setAttribute('disabled', 'true');
        }
    }

    // logika konfirmasi bayar (kirim ke backend/python)
    if (confirmPayBtn) {
        confirmPayBtn.addEventListener('click', async () => {
    
            if(loadingOverlay) loadingOverlay.style.display = 'flex';
            
            setTimeout(async () => {
                try {
                    const response = await fetch('/book_ticket', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ movie_id: movieId, seats: selectedSeats })
                    });
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        window.location.href = "/history";
                    } else {
                        alert(result.msg);
                        if(loadingOverlay) loadingOverlay.style.display = 'none';
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Terjadi kesalahan koneksi.');
                    if(loadingOverlay) loadingOverlay.style.display = 'none';
                }
            }, 1000);
        });
    }
});
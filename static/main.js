// ================= ฟังก์ชันส่วนกลาง (Global Utilities) =================
const getSafeUser = () => {
    try {
        const stored = localStorage.getItem('user');
        if (stored && stored !== 'undefined') return JSON.parse(stored);
    } catch (e) {
        console.warn("เคลียร์ข้อมูลล็อกอินที่เสียหาย");
        localStorage.removeItem('user');
    }
    return null;
};

const openModal = (id) => {
    const modal = document.getElementById(id);
    if(modal) modal.style.display = 'flex';
};
const closeModal = (id) => {
    const modal = document.getElementById(id);
    if(modal) modal.style.display = 'none';
};

// ================= ระบบเปลี่ยนธีม (Dark / Light Mode) =================
const toggleTheme = () => {
    const root = document.documentElement;
    const icon = document.getElementById('theme-icon');
    if (root.getAttribute('data-theme') === 'light') {
        root.removeAttribute('data-theme');
        localStorage.setItem('theme', 'dark');
        if(icon) icon.className = 'fa-solid fa-sun';
    } else {
        root.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        if(icon) icon.className = 'fa-solid fa-moon';
    }
};

// ดึงค่าธีมทันที
(() => {
    if (localStorage.getItem('theme') === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
    }
})();


// ================= ฟังก์ชัน Authentication & UI Status =================
const toggleInspectZone = (isAllowed) => {
    const btnInspect = document.getElementById('btn-inspect');
    const refDropzone = document.getElementById('ref-dropzone');
    const candDropzone = document.getElementById('cand-dropzone');
    const btnGenId = document.getElementById('btn-gen-id');
    const btnClearHistory = document.getElementById('btn-clear-history');

    if (isAllowed) {
        if(btnInspect) { btnInspect.disabled = false; btnInspect.style.opacity = '1'; btnInspect.style.cursor = 'pointer'; btnInspect.style.pointerEvents = 'auto'; }
        if(btnGenId) { btnGenId.disabled = false; btnGenId.style.opacity = '1'; btnGenId.style.pointerEvents = 'auto'; }
        if(refDropzone) { refDropzone.style.opacity = '1'; refDropzone.style.pointerEvents = 'auto'; }
        if(candDropzone) { candDropzone.style.opacity = '1'; candDropzone.style.pointerEvents = 'auto'; }
        if(btnClearHistory) { btnClearHistory.style.display = 'inline-flex'; } 
    } else {
        if(btnInspect) { btnInspect.disabled = true; btnInspect.style.opacity = '0.3'; btnInspect.style.cursor = 'not-allowed'; btnInspect.style.pointerEvents = 'none'; }
        if(btnGenId) { btnGenId.disabled = true; btnGenId.style.opacity = '0.3'; btnGenId.style.pointerEvents = 'none'; }
        if(refDropzone) { refDropzone.style.opacity = '0.3'; refDropzone.style.pointerEvents = 'none'; }
        if(candDropzone) { candDropzone.style.opacity = '0.3'; candDropzone.style.pointerEvents = 'none'; }
        if(btnClearHistory) { btnClearHistory.style.display = 'none'; } 
    }
};

const checkLoginStatus = () => {
    const user = getSafeUser();
    const navAuth = document.getElementById('nav-auth-section');
    const clearBtn = document.getElementById('btn-clear-history');
    const manageUsersBtn = document.getElementById('btn-manage-users');

    if (user) {
        let roleTh = user.role === 'seller' ? 'ผู้ขาย' : (user.role === 'buyer' ? 'ผู้ซื้อ' : 'แอดมิน');
        if(navAuth) {
            navAuth.innerHTML = `
                <span class="user-badge"><i class="fa-solid fa-user-circle"></i> ${user.username} (${roleTh})</span>
                <button class="btn-text text-danger" onclick="logout()">ออกจากระบบ</button>
            `;
        }

        if (user.role === 'seller' || user.role === 'admin') {
            document.getElementById('btn-show-add-amulet').style.display = 'inline-flex';
            toggleInspectZone(true);
        } else {
            document.getElementById('btn-show-add-amulet').style.display = 'none';
            toggleInspectZone(false); 
        }

        if (clearBtn) {
            clearBtn.style.display = (user.role === 'admin' || user.username === 'admin') ? 'inline-flex' : 'none';
        }
        if (manageUsersBtn) {
            manageUsersBtn.style.display = (user.role === 'admin' || user.username === 'admin') ? 'inline-block' : 'none';
        }
    } else {
        if(navAuth) {
            navAuth.innerHTML = `
                <button class="btn-text" onclick="openModal('login-modal')">เข้าสู่ระบบ</button>
                <button class="btn-primary" onclick="openModal('register-modal')">สมัครสมาชิก</button>
            `;
        }
        toggleInspectZone(false); 
        if (clearBtn) clearBtn.style.display = 'none';
        if (manageUsersBtn) manageUsersBtn.style.display = 'none';
    }

    if (typeof window.fetchMarketplace === 'function') {
        window.fetchMarketplace();
    }
};

window.submitRegister = async () => {
    const u = document.getElementById('reg-username').value.trim();
    const e = document.getElementById('reg-email').value.trim();
    const p = document.getElementById('reg-password').value.trim();
    const r = document.getElementById('reg-role').value;

    if (!u || !e || !p) return alert("กรุณากรอกข้อมูลให้ครบถ้วน");

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, email: e, password: p, role: r})
        });
        const data = await res.json();
        alert(data.message);
        if (data.success) {
            closeModal('register-modal');
            openModal('login-modal');
        }
    } catch (err) {
        alert("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    }
};

window.submitLogin = async () => {
    // ✨ ดึงค่าจากช่องอีเมลแทนช่องชื่อ
    const e = document.getElementById('log-email').value.trim();
    const p = document.getElementById('log-password').value.trim();

    if (!e || !p) return alert("กรุณากรอกข้อมูลให้ครบถ้วน");

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email: e, password: p}) // ส่งอีเมลไปหลังบ้าน
        });
        const data = await res.json();
        
        if (data.success) {
            const userData = data.user || { id: data.user_id, username: data.username, role: data.role };
            localStorage.setItem('user', JSON.stringify(userData));
            alert(data.message || "เข้าสู่ระบบสำเร็จ!");
            
            closeModal('login-modal');
            checkLoginStatus(); 
            if(window.fetchMarketplace) window.fetchMarketplace();
        } else {
            alert(data.message || "อีเมลหรือรหัสผ่านไม่ถูกต้อง");
        }
    } catch (err) {
        alert("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    }
};

window.logout = () => {
    if(confirm('ต้องการออกจากระบบใช่หรือไม่?')) {
        localStorage.removeItem('user');
        checkLoginStatus();
        alert('ออกจากระบบเรียบร้อย');
        if(window.fetchMarketplace) window.fetchMarketplace();
    }
};


// ================= ระบบจัดการสมาชิก (เฉพาะ Admin) =================
window.openUserManagement = () => {
    openModal('manage-users-modal');
    window.fetchUsersList(); 
};

window.fetchUsersList = async () => {
    const container = document.getElementById('users-list-container');
    container.innerHTML = '<p style="text-align: center; color: var(--color-text);">กำลังโหลดข้อมูล...</p>';
    
    try {
        const response = await fetch('/api/users'); 
        if (!response.ok) throw new Error('Network response was not ok');
        
        const users = await response.json();
        if (users.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--color-text);">ยังไม่มีสมาชิกในระบบ</p>';
            return;
        }

        let html = `
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem;">
                <thead>
                    <tr style="border-bottom: 2px solid #ddd;">
                        <th style="padding: 10px; text-align: left;">ชื่อผู้ใช้</th>
                        <th style="padding: 10px; text-align: left;">อีเมล</th>
                        <th style="padding: 10px; text-align: left;">บทบาท</th>
                        <th style="padding: 10px; text-align: center;">จัดการ</th>
                    </tr>
                </thead>
                <tbody>
        `;

        users.forEach(u => {
            let roleTh = u.role === 'seller' ? 'ผู้ขาย' : (u.role === 'buyer' ? 'ผู้ซื้อ' : 'แอดมิน');
            html += `
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px;">${u.username}</td>
                    <td style="padding: 10px; color: #666;">${u.email}</td>
                    <td style="padding: 10px;">
                        <span class="user-badge" style="font-size: 0.8rem; padding: 2px 6px;">${roleTh}</span>
                    </td>
                    <td style="padding: 10px; text-align: center;">
                        ${u.username === 'admin' 
                            ? '<span style="color: #aaa;">-</span>' 
                            // ✨ แก้ไขตรงนี้: ใส่เครื่องหมายคำพูดครอบ '${u.id}' ป้องกันโค้ดพัง
                            : `<button class="btn-text text-danger" style="padding: 2px 5px;" onclick="deleteUser('${u.id}', '${u.username}')"><i class="fa-solid fa-trash"></i> ลบ</button>`
                        }
                    </td>
                </tr>
            `;
        });
        html += `</tbody></table>`;
        container.innerHTML = html; 

    } catch (error) {
        console.error('Error fetching users:', error);
        container.innerHTML = '<p style="text-align: center; color: red;">ไม่สามารถดึงข้อมูลได้ กรุณาตรวจสอบ API หลังบ้าน</p>';
    }
};

window.deleteUser = async (userId, username) => {
    // ✨ ดักจับตรงนี้! ถ้า ID พัง มันจะเด้งเตือนเราทันที
    if (!userId || userId === 'undefined') {
        alert("❌ ระบบหา ID ไม่เจอ!\n(แสดงว่าหลังบ้านยังเป็นโค้ดเก่าอยู่ หรือลืมรีสตาร์ทเซิร์ฟเวอร์จอดำครับ)");
        return;
    }

    if (confirm(`คุณแน่ใจหรือไม่ว่าต้องการลบบัญชี "${username}" ทิ้งถาวร?`)) {
        try {
            const response = await fetch(`/api/users/${userId}`, { method: 'DELETE' });
            
            if (response.ok) {
                // โหลดตารางใหม่เงียบๆ โดยไม่รีเฟรชหน้าเว็บ
                if (typeof window.fetchUsersList === 'function') {
                    window.fetchUsersList(); 
                }
            } else {
                const data = await response.json();
                alert(data.message || 'ไม่สามารถลบสมาชิกได้');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            alert('เกิดข้อผิดพลาดในการเชื่อมต่อ');
        }
    }
};


// ================= ระบบตลาดพระเครื่อง (Marketplace) =================
window.markAsSold = async (id) => {
    if(!confirm("ยืนยันการทำรายการนี้ใช่หรือไม่?")) return;
    try {
        const res = await fetch(`/api/amulets/${id}/sold`, { method: 'POST' });
        const data = await res.json();
        if(data.success) {
            fetchMarketplace(); // โหลดตลาดใหม่เพื่อโชว์ป้าย SOLD
        } else {
            alert("เกิดข้อผิดพลาด: " + data.message);
        }
    } catch (err) {
        alert("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้");
    }
};

window.fetchMarketplace = async () => {
    const grid = document.getElementById('marketplace-grid');
    if (!grid) return;

    try {
        const user = getSafeUser();
        const isAdmin = user && (user.role === 'admin' || user.username === 'admin');

        const res = await fetch('/api/amulets');
        if (!res.ok) throw new Error("เซิร์ฟเวอร์หลังบ้านมีปัญหา");
        
        const data = await res.json();

        if (data.success && data.amulets.length > 0) {
            grid.innerHTML = ''; 
            
            data.amulets.forEach(amulet => {
                const card = document.createElement('div');
                card.className = 'market-card card';
                card.style.padding = '15px';
                card.style.display = 'flex';
                card.style.flexDirection = 'column';
                card.style.gap = '10px';
                card.style.position = 'relative'; 
                
                const contactData = amulet.description || 'ไม่ได้ระบุ';
                const isOwner = user && (user.id == amulet.seller_id || user.user_id == amulet.seller_id);
                const isSold = amulet.status === 'sold'; 
                
                let actionButtons = '';
                // ✨ อัปเดตให้รูปภาพทั้งหมด สามารถชี้แล้วเด้ง (hover) และคลิกได้
                let imageStyle = "width: 100%; height: 200px; object-fit: cover; border-radius: 8px; cursor: pointer; transition: transform 0.2s;";
                let soldStamp = "";
                
                if (isSold) {
                    imageStyle += " filter: grayscale(100%); opacity: 0.6;";
                    // ✨ เพิ่ม pointer-events: none; ให้ป้าย SOLD เพื่อให้คลิกทะลุไปโดนรูปภาพได้
                    soldStamp = `<div style="position: absolute; top: 35%; left: 50%; transform: translate(-50%, -50%) rotate(-15deg); background: rgba(220, 38, 38, 0.9); color: white; padding: 10px 25px; font-size: 2rem; font-weight: 900; border: 4px solid white; border-radius: 10px; z-index: 10; letter-spacing: 2px; pointer-events: none;">SOLD</div>`;
                    
                    if (isAdmin || isOwner) {
                        actionButtons = `<button class="btn-danger" style="padding: 5px 10px; font-size: 0.8rem; background-color: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;" onclick="deleteAmulet(${amulet.id})"><i class="fa-solid fa-trash"></i> ลบโพสต์</button>`;
                    } else {
                        actionButtons = `<span style="color: #ef4444; font-weight: bold; font-size: 0.9rem;">ขายแล้ว</span>`;
                    }
                } else {
                    let buyBtnHTML = '';
                    if (user && !isOwner) { 
                        buyBtnHTML = `<button style="padding: 5px 10px; font-size: 0.8rem; background-color: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px;" onclick="markAsSold(${amulet.id})">🛒 ซื้อเลย</button>`;
                    } else if (user && isOwner) { 
                        buyBtnHTML = `<button style="padding: 5px 10px; font-size: 0.8rem; background-color: #f59e0b; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px;" onclick="markAsSold(${amulet.id})">ปิดการขาย</button>`;
                    }
                    
                    let deleteBtnHTML = '';
                    if (isAdmin || isOwner) {
                        deleteBtnHTML = `<button class="btn-danger" style="padding: 5px 10px; font-size: 0.8rem; margin-left: 5px; background-color: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;" onclick="deleteAmulet(${amulet.id})"><i class="fa-solid fa-trash"></i> ลบ</button>`;
                    }
                    
                    actionButtons = `
                        <div style="display: flex;">
                            ${buyBtnHTML}
                            <button style="padding: 5px 10px; font-size: 0.8rem; background-color: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;" onclick="showContactInfo('${amulet.seller_name}', '${contactData}')">สนใจติดต่อ</button>
                            ${deleteBtnHTML}
                        </div>
                    `;
                }

                // ✨ ปลดล็อก onclick ให้ทำงานกับทุกรูปภาพ
                card.innerHTML = `
                    ${soldStamp}
                    <img src="${amulet.image_path}" alt="${amulet.name}" 
                         style="${imageStyle}" 
                         onclick="viewMarketImage('${amulet.image_path}', '${amulet.name}')"
                         onmouseover="this.style.transform='scale(1.02)'" 
                         onmouseout="this.style.transform='scale(1)'"
                         title="คลิกเพื่อดูรูปขนาดเต็ม">
                         
                    <h3 class="market-title" style="margin: 0; font-size: 1.2rem;">${amulet.name}</h3>
                    <p class="market-temple" style="margin: 0; font-size: 0.9rem;">
                        <i class="fa-solid fa-location-dot"></i> วัด/กรุ: ${amulet.temple || 'ไม่ระบุ'}
                    </p>
                    <p class="market-seller" style="margin: 0; font-size: 0.9rem;">
                        <i class="fa-solid fa-user"></i> ผู้ลงขาย: ${amulet.seller_name}
                    </p>
                    <div style="margin-top: auto; padding-top: 10px; border-top: 1px solid var(--color-border); display: flex; justify-content: space-between; align-items: center;">
                        <span class="market-price" style="font-weight: bold; font-size: 1.1rem; color: #d97706;">
                            ฿${Number(amulet.price).toLocaleString()}
                        </span>
                        <div style="display: flex; align-items: center;">
                            ${actionButtons}
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        } else {
            grid.innerHTML = '<p style="color: var(--color-text-muted); grid-column: 1 / -1; text-align: center;">ยังไม่มีพระเครื่องลงขายในขณะนี้</p>';
        }
    } catch (err) {
        console.error("Error fetching marketplace:", err);
        grid.innerHTML = '<p style="color: #ef4444; grid-column: 1 / -1; text-align: center;">พบปัญหาขัดข้อง: ไม่สามารถดึงข้อมูลตลาดได้</p>';
    }
};

window.submitAddAmulet = async () => {
    try {
        const user = getSafeUser();
        if (!user || user.role !== 'seller') {
            return alert('เฉพาะผู้ขายเท่านั้นที่ลงประกาศได้ครับ');
        }

        const name = document.getElementById('market-name').value.trim();
        const temple = document.getElementById('market-temple').value.trim();
        const year = document.getElementById('market-year').value.trim();
        const price = document.getElementById('market-price').value.trim();
        const contact = document.getElementById('market-contact').value.trim(); 
        const imgFile = document.getElementById('market-img').files[0];

        if (!name || !contact || !imgFile) {
            return alert('กรุณากรอกช่องทางการติดต่อ ชื่อพระเครื่อง และแนบรูปภาพให้ครบถ้วนครับ');
        }

        const sellerId = user.id || user.user_id; 
        if (!sellerId) return alert('ไม่พบข้อมูล ID ของผู้ขาย กรุณาล็อกอินใหม่อีกครั้งครับ');

        const formData = new FormData();
        formData.append('seller_id', sellerId);
        formData.append('name', name);
        formData.append('temple', temple);
        formData.append('year', year);
        formData.append('price', price || 0);
        formData.append('description', contact); 
        formData.append('image', imgFile);

        const res = await fetch('/api/amulets/add', { method: 'POST', body: formData });
        
        if (!res.ok) return alert("ระบบหลังบ้านปฏิเสธการรับข้อมูล");

        const data = await res.json();
        alert(data.message || "ลงประกาศขายพระเครื่องสำเร็จ!");
        
        if (data.success) {
            closeModal('add-amulet-modal');
            window.fetchMarketplace(); 
        }
    } catch (err) {
        console.error("JavaScript Error:", err);
        alert("เกิดข้อผิดพลาดในการทำงานของหน้าเว็บครับ");
    }
};

window.deleteAmulet = async (amuletId) => {
    if (!confirm('แน่ใจหรือไม่ว่าต้องการลบพระเครื่องรายการนี้ออกจากตลาด?')) return;
    try {
        // ✨ ดึงข้อมูลผู้ใช้งานปัจจุบันเพื่อเอาค่า role ส่งไปให้หลังบ้านตรวจสอบ
        const user = getSafeUser();
        const userRole = user ? user.role : '';

        // ✨ แนบ ?role=${userRole} ไปกับ URL ด้วย
        const res = await fetch(`/api/amulets/${amuletId}?role=${userRole}`, { method: 'DELETE' });
        const data = await res.json();
        
        if (data.success) {
            alert(data.message || 'ลบรายการสำเร็จครับ!');
            window.fetchMarketplace(); 
        } else {
            alert(data.message || 'ลบไม่สำเร็จ');
        }
    } catch (err) {
        console.error("Delete Error:", err);
        alert("เกิดข้อผิดพลาดในการเชื่อมต่อกับระบบหลังบ้านครับ");
    }
};

window.viewMarketImage = (src, name) => {
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img');
    const caption = document.getElementById('modal-caption');
    
    if (modal && modalImg) {
        modal.style.display = "flex"; 
        modal.style.flexDirection = "column";
        modal.style.alignItems = "center";
        modal.style.justifyContent = "center";

        modalImg.src = src;
        modalImg.style.margin = "auto";
        modalImg.style.display = "block";
        
        if (caption) {
            caption.innerText = name;
            caption.style.textAlign = "center";
            caption.style.marginTop = "15px";
        }
    }
};

window.showContactInfo = (sellerName, contactData) => {
    const nameElem = document.getElementById('show-seller-name');
    const infoElem = document.getElementById('show-contact-info');
    
    if (nameElem && infoElem) {
        nameElem.innerText = sellerName || "ไม่ทราบชื่อ";
        infoElem.innerText = contactData || "ไม่มีข้อมูลติดต่อ";
        openModal('contact-modal');
    }
};


// ================= Core System Initializer (ทำงานเมื่อเปิดเว็บ) =================
document.addEventListener('DOMContentLoaded', () => {
    
    checkLoginStatus(); 
    if(window.fetchMarketplace) window.fetchMarketplace();

    // อัปเดตไอคอนธีม
    const savedTheme = localStorage.getItem('theme');
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.className = savedTheme === 'light' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
    }

    // ================= ส่วนของการตรวจสอบภาพอ้างอิง =================
    const amuletIdInput = document.getElementById('amulet-id');
    const btnGenId = document.getElementById('btn-gen-id');
    const btnInspect = document.getElementById('btn-inspect');

    const refFile = document.getElementById('ref-file');
    const refDropzone = document.getElementById('ref-dropzone');
    const refPlaceholder = document.getElementById('ref-placeholder');
    const refPreviewContainer = document.getElementById('ref-preview-container');
    const refImgPreview = document.getElementById('ref-img-preview');
    const btnRemoveRef = document.getElementById('btn-remove-ref');

    const candFile = document.getElementById('cand-file');
    const candDropzone = document.getElementById('cand-dropzone');
    const candPlaceholder = document.getElementById('cand-placeholder');
    const candPreviewContainer = document.getElementById('cand-preview-container');
    const candImgPreview = document.getElementById('cand-img-preview');
    const btnRemoveCand = document.getElementById('btn-remove-cand');

    const resultDecision = document.getElementById('result-decision');
    const decisionWrapper = document.querySelector('.decision-box-wrapper');
    const resultScore = document.getElementById('result-score');
    const scoreProgress = document.getElementById('score-progress');
    const resultNotes = document.getElementById('result-notes');
    const imgOverlay = document.getElementById('img-overlay');
    const imgRefContour = document.getElementById('img-ref-contour');
    
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    const overlayPlaceholder = document.getElementById('overlay-placeholder');
    const overlayImageContainer = document.getElementById('overlay-image-container');
    const refContourPlaceholder = document.getElementById('ref-contour-placeholder');
    const refContourImageContainer = document.getElementById('ref-contour-image-container');

    const historySearch = document.getElementById('history-search');
    const btnRefreshHistory = document.getElementById('btn-refresh-history');
    const btnClearHistory = document.getElementById('btn-clear-history');
    const historyCount = document.getElementById('history-count');
    const historyGalleryContainer = document.getElementById('history-gallery-container');
    const historyTableBody = document.getElementById('history-table-body');

    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const stepPreprocess = document.getElementById('step-preprocess');
    const stepAlign = document.getElementById('step-align');
    const stepScore = document.getElementById('step-score');

    const imageModal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img');
    const modalCaption = document.getElementById('modal-caption');
    const modalClose = document.querySelector('.modal-close');

    const THRESHOLD = 24.0;

    const generateRandomId = () => {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const num = Math.floor(1000 + Math.random() * 9000);
        const prefixIndex = Math.floor(Math.random() * chars.length);
        const prefix = chars[prefixIndex] + chars[(prefixIndex + 7) % chars.length];
        if(amuletIdInput) amuletIdInput.value = `AMU-${prefix}-${num}`;
    };

    if(btnGenId) btnGenId.addEventListener('click', generateRandomId);

    const setupDragAndDrop = (dropzone, fileInput, placeholder, previewContainer, imgPreview, fileKey) => {
        if(!dropzone) return;
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, e => e.preventDefault(), false);
        });
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
        });

        dropzone.addEventListener('drop', e => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length) {
                fileInput.files = files;
                handleFileSelection(files[0], placeholder, previewContainer, imgPreview);
                if (fileKey === 'cand') generateRandomId();
            }
        });

        dropzone.addEventListener('click', (e) => {
            if (e.target.closest('.btn-remove-file')) return;
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                handleFileSelection(fileInput.files[0], placeholder, previewContainer, imgPreview);
                if (fileKey === 'cand') generateRandomId();
            }
        });
    };

    const handleFileSelection = (file, placeholder, previewContainer, imgPreview) => {
        if (!file.type.startsWith('image/')) return alert('กรุณาอัปโหลดเฉพาะไฟล์รูปภาพ');
        const reader = new FileReader();
        reader.onload = (e) => {
            imgPreview.src = e.target.result;
            placeholder.classList.add('hidden');
            previewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    };

    const resetUploadZone = (fileInput, placeholder, previewContainer, imgPreview) => {
        fileInput.value = '';
        imgPreview.src = '';
        previewContainer.classList.add('hidden');
        placeholder.classList.remove('hidden');
    };

    setupDragAndDrop(refDropzone, refFile, refPlaceholder, refPreviewContainer, refImgPreview, 'ref');
    setupDragAndDrop(candDropzone, candFile, candPlaceholder, candPreviewContainer, candImgPreview, 'cand');

    if(btnRemoveRef) btnRemoveRef.addEventListener('click', () => resetUploadZone(refFile, refPlaceholder, refPreviewContainer, refImgPreview));
    if(btnRemoveCand) btnRemoveCand.addEventListener('click', () => resetUploadZone(candFile, candPlaceholder, candPreviewContainer, candImgPreview));

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            tabPanels.forEach(panel => {
                if (panel.id === targetTab) panel.classList.add('active');
                else panel.classList.remove('active');
            });
        });
    });

    const showLoading = () => {
        loadingOverlay.classList.remove('hidden');
        stepPreprocess.className = 'loading-step active';
        stepPreprocess.querySelector('i').className = 'fa-solid fa-spinner fa-spin';
        stepAlign.className = 'loading-step';
        stepAlign.querySelector('i').className = 'fa-solid fa-circle';
        stepScore.className = 'loading-step';
        stepScore.querySelector('i').className = 'fa-solid fa-circle';
        loadingText.textContent = 'กำลังเริ่มต้นปรับแต่งภาพและประมวลผลรูปร่าง...';

        setTimeout(() => {
            stepPreprocess.className = 'loading-step done';
            stepPreprocess.querySelector('i').className = 'fa-solid fa-circle-check';
            stepAlign.className = 'loading-step active';
            stepAlign.querySelector('i').className = 'fa-solid fa-spinner fa-spin';
            loadingText.textContent = 'กำลังจัดแนวรูปภาพด้วยโฮโมกราฟี (Perspective Warp)...';
        }, 1200);

        setTimeout(() => {
            stepAlign.className = 'loading-step done';
            stepAlign.querySelector('i').className = 'fa-solid fa-circle-check';
            stepScore.className = 'loading-step active';
            stepScore.querySelector('i').className = 'fa-solid fa-spinner fa-spin';
            loadingText.textContent = 'กำลังคำนวณคะแนนความคลาดเคลื่อนจุดต่อจุด...';
        }, 2400);
    };

    const hideLoading = () => loadingOverlay.classList.add('hidden');

    if(btnInspect) {
        btnInspect.addEventListener('click', async () => {
            const user = getSafeUser();
            if (!user || (user.role !== 'seller' && user.role !== 'admin')) {
                alert('ฟังก์ชันนี้สงวนสิทธิ์ไว้เฉพาะ "ผู้ขาย" หรือ "แอดมิน" เท่านั้นครับ');
                return; 
            }

            if (!refFile.files.length) return alert('กรุณาอัปโหลดภาพอ้างอิง (REF) ก่อนทำการตรวจ');
            
            showLoading();

            const formData = new FormData();
            formData.append('amulet_id', amuletIdInput.value.trim());
            formData.append('ref_file', refFile.files[0]);
            formData.append('cand_file', candFile.files[0]);

            try {
                const response = await fetch('/api/inspect', { method: 'POST', body: formData });
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                    fetchHistory();
                } else {
                    alert(`ตรวจพบบางอย่างผิดปกติ: ${data.error_message}`);
                }
            } catch (error) {
                alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
            } finally {
                hideLoading();
            }
        });
    }

    const displayResults = (data) => {
        resultDecision.textContent = data.decision;
        decisionWrapper.className = 'stat-box decision-box-wrapper'; 
        
        if (data.decision === 'PASS') {
            decisionWrapper.classList.add('pass');
            resultDecision.className = 'stat-value state-pass';
        } else if (data.decision === 'FAIL') {
            decisionWrapper.classList.add('fail');
            resultDecision.className = 'stat-value state-fail';
        } else {
            resultDecision.className = 'stat-value state-waiting';
        }

        const scoreVal = parseFloat(data.score);
        if (!isNaN(scoreVal)) {
            resultScore.textContent = `${scoreVal.toFixed(3)} px`;
            const percent = Math.min((scoreVal / THRESHOLD) * 100, 100);
            scoreProgress.style.width = `${percent}%`;
            scoreProgress.className = `progress-bar ${data.decision === 'PASS' ? 'pass' : 'fail'}`;
        } else {
            resultScore.textContent = data.score || '-';
            scoreProgress.style.width = '0%';
        }

        resultNotes.textContent = data.note || '';

        if (data.overlay_url) {
            imgOverlay.src = `${data.overlay_url}?t=${new Date().getTime()}`;
            overlayPlaceholder.classList.add('hidden');
            overlayImageContainer.classList.remove('hidden');
        } else {
            overlayImageContainer.classList.add('hidden');
            overlayPlaceholder.classList.remove('hidden');
        }

        if (data.ref_contour_url) {
            imgRefContour.src = `${data.ref_contour_url}?t=${new Date().getTime()}`;
            refContourPlaceholder.classList.add('hidden');
            refContourImageContainer.classList.remove('hidden');
        } else {
            refContourImageContainer.classList.add('hidden');
            refContourPlaceholder.classList.remove('hidden');
        }

        document.querySelector('.tab-btn[data-tab="tab-overlay"]').click();
    };

    const fetchHistory = async () => {
        if(!historySearch) return;
        const q = historySearch.value.trim();
        try {
            const response = await fetch(`/api/history?q=${encodeURIComponent(q)}`);
            const data = await response.json();
            historyCount.textContent = `พบทั้งหมด ${data.count} รายการ`;
            renderGallery(data.gallery);
            renderTable(data.table);
        } catch (error) { console.error(error); }
    };

    const renderGallery = (galleryItems) => {
        if (!galleryItems || galleryItems.length === 0) {
            historyGalleryContainer.innerHTML = '<div class="gallery-empty">ไม่มีภาพประวัติการตรวจ</div>';
            return;
        }
        historyGalleryContainer.innerHTML = '';
        galleryItems.forEach(item => {
            const galleryCard = document.createElement('div');
            galleryCard.className = 'gallery-item';
            const badgeClass = item.decision === 'PASS' ? 'pass' : 'fail';
            
            galleryCard.innerHTML = `
                <div class="thumb-image-wrapper">
                    <img src="${item.overlay_path}" alt="Amulet overlay" loading="lazy">
                    <span class="thumb-decision-badge ${badgeClass}">${item.decision}</span>
                </div>
                <div class="thumb-info">
                    <div class="thumb-id" title="${item.amulet_id}">${item.amulet_id}</div>
                    <div class="thumb-meta"><span>score: ${parseFloat(item.score).toFixed(3)} px</span></div>
                </div>
            `;
            galleryCard.addEventListener('click', () => {
                const openImageModalObj = document.getElementById('image-modal');
                const mImg = document.getElementById('modal-img');
                const mCap = document.getElementById('modal-caption');
                if (openImageModalObj && mImg) {
                    mImg.src = item.overlay_path;
                    mCap.textContent = `${item.amulet_id} - ${item.decision} | score: ${parseFloat(item.score).toFixed(3)} px`;
                    openImageModalObj.style.display = 'block';
                    document.body.style.overflow = 'hidden';
                }
            });
            historyGalleryContainer.appendChild(galleryCard);
        });
    };

    const renderTable = (rows) => {
        if (!rows || rows.length === 0) {
            historyTableBody.innerHTML = `<tr><td colspan="7" class="table-empty">ไม่พบประวัติการทดสอบ</td></tr>`;
            return;
        }
        historyTableBody.innerHTML = '';
        rows.forEach(row => {
            const tr = document.createElement('tr');
            const decisionClass = row.decision === 'PASS' ? 'pass' : 'fail';
            const formattedScore = !isNaN(parseFloat(row.score_px)) ? parseFloat(row.score_px).toFixed(3) : row.score_px;
            tr.innerHTML = `
                <td>${row.timestamp || ''}</td>
                <td style="font-weight: 500;">${row.amulet_id || ''}</td>
                <td>${formattedScore} px</td>
                <td class="table-decision-cell ${decisionClass}">${row.decision || ''}</td>
                <td>${row.threshold_px || ''} px</td>
                <td>${row.num_pstar || ''}</td>
                <td style="color: var(--color-text-muted); font-size: 0.8rem;">${row.scoring_method || ''}</td>
            `;
            historyTableBody.appendChild(tr);
        });
    };

    if(btnClearHistory) {
        btnClearHistory.addEventListener('click', async () => {
            const user = getSafeUser();
            if (!user || (user.role !== 'seller' && user.role !== 'admin')) {
                alert('สิทธิ์การล้างประวัติสงวนไว้สำหรับ "ผู้ขาย" หรือ "แอดมิน" เท่านั้นครับ');
                return;
            }

            if (!confirm('แน่ใจหรือไม่ที่จะลบประวัติทั้งหมด?')) return;
            try {
                const response = await fetch('/api/clear-history', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert(data.message);
                    fetchHistory();
                    resultDecision.textContent = '-';
                    decisionWrapper.className = 'stat-box decision-box-wrapper';
                    resultDecision.className = 'stat-value state-waiting';
                    resultScore.textContent = '-';
                    scoreProgress.style.width = '0%';
                    resultNotes.textContent = 'ล้างข้อมูลแล้ว';
                    overlayImageContainer.classList.add('hidden');
                    overlayPlaceholder.classList.remove('hidden');
                    refContourImageContainer.classList.add('hidden');
                    refContourPlaceholder.classList.remove('hidden');
                }
            } catch (error) { alert('เกิดปัญหาในการลบประวัติ'); }
        });
    }

    if(btnRefreshHistory) btnRefreshHistory.addEventListener('click', fetchHistory);

    let searchTimeout = null;
    if(historySearch) {
        historySearch.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(fetchHistory, 300);
        });
    }

    if(modalClose) {
        modalClose.addEventListener('click', () => {
            if(imageModal) imageModal.style.display = 'none';
            document.body.style.overflow = '';
            if(modalImg) modalImg.src = '';
        });
    }

    if(imageModal) {
        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal || e.target.classList.contains('modal-content-wrapper')) {
                imageModal.style.display = 'none';
                document.body.style.overflow = '';
                if(modalImg) modalImg.src = '';
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && imageModal && imageModal.style.display === 'block') {
            imageModal.style.display = 'none';
            document.body.style.overflow = '';
            if(modalImg) modalImg.src = '';
        }
    });

    if(imgOverlay) {
        imgOverlay.addEventListener('click', () => {
            const idText = amuletIdInput.value.trim() || 'AUTO';
            if (imageModal && modalImg && modalCaption) {
                modalImg.src = imgOverlay.src;
                modalCaption.textContent = `ผลการเทียบ overlay: ID=${idText} | ผลลัพธ์=${resultDecision.textContent} | Score=${resultScore.textContent}`;
                imageModal.style.display = 'block';
                document.body.style.overflow = 'hidden';
            }
        });
    }

    if(imgRefContour) {
        imgRefContour.addEventListener('click', () => {
            const idText = amuletIdInput.value.trim() || 'AUTO';
            if (imageModal && modalImg && modalCaption) {
                modalImg.src = imgRefContour.src;
                modalCaption.textContent = `ภาพอ้างอิงต้นฉบับ Contour & P* Points: ID=${idText}`;
                imageModal.style.display = 'block';
                document.body.style.overflow = 'hidden';
            }
        });
    }

    generateRandomId();
    fetchHistory();

    // ================= บังคับสีให้ตาราง PASS / FAIL =================
    const forceStatusColors = () => {
        const cells = document.querySelectorAll('#table-history td, .stat-value');
        cells.forEach(td => {
            const text = td.textContent.trim();
            if (text === 'PASS') {
                td.style.setProperty('color', '#10b981', 'important'); 
                td.style.setProperty('font-weight', 'bold', 'important');
            } else if (text === 'FAIL') {
                td.style.setProperty('color', '#ef4444', 'important'); 
                td.style.setProperty('font-weight', 'bold', 'important');
            }
        });
    };

    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => setTimeout(forceStatusColors, 50));
    }

    if (historyTableBody) {
        new MutationObserver(forceStatusColors).observe(historyTableBody, { childList: true, subtree: true });
    }
    setTimeout(forceStatusColors, 500);
});

// ================= ระบบตรวจสอบสิทธิ์ (แอบเช็กทุก 0.5 วินาที) =================
const applyRolePermissions = () => {
    const user = getSafeUser();
    document.querySelectorAll('button').forEach(btn => {
        if (btn.textContent.includes('ลงขายพระเครื่อง')) {
            if (!user || (user.role !== 'admin' && user.role !== 'seller')) {
                btn.style.display = 'none';
            } else {
                btn.style.display = ''; 
            }
        }
    });
};
setInterval(applyRolePermissions, 500);
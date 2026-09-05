const CART_KEY='fitgear_cart';
let cart=JSON.parse(localStorage.getItem(CART_KEY)||'[]');
function saveCart(){localStorage.setItem(CART_KEY,JSON.stringify(cart));updateCartCount();renderCart()}
function updateCartCount(){const n=cart.reduce((s,x)=>s+x.qty,0);const el=document.getElementById('cart-count');if(el)el.textContent=n;const label=document.getElementById('cart-count-label');if(label)label.textContent=`(${n})`}
function addToCart(id,name,price,image=''){const item=cart.find(x=>x.id==id);if(item)item.qty++;else cart.push({id,name,price:Number(price),image,qty:1});saveCart();openCart();toast(`${name} added to cart`)}
function changeQty(id,delta){const item=cart.find(x=>x.id==id);if(!item)return;item.qty+=delta;if(item.qty<=0)cart=cart.filter(x=>x.id!=id);saveCart()}
function removeFromCart(id){cart=cart.filter(x=>x.id!=id);saveCart()}
function renderCart(){const box=document.getElementById('cart-items');const total=document.getElementById('cart-total');if(!box)return;if(!cart.length){box.innerHTML='<div style="padding:60px 0;text-align:center;color:#7b847a;font-size:12px">Your cart is empty.<br><br><b>Add some gear and your bag will appear here.</b></div>';total.textContent='EGP 0';return}
box.innerHTML=cart.map(x=>`<div class="cart-row"><img src="${escapeAttr(x.image||'')}" alt=""><div class="cart-row-info"><b>${escapeHtml(x.name)}</b><small>EGP ${Number(x.price).toLocaleString()} each</small><div class="qty-control"><button onclick="changeQty(${x.id},-1)">−</button><span>${x.qty}</span><button onclick="changeQty(${x.id},1)">+</button></div></div><div><div class="cart-row-price">EGP ${(x.price*x.qty).toLocaleString()}</div><button class="cart-remove" onclick="removeFromCart(${x.id})">Remove</button></div></div>`).join('');
total.textContent='EGP '+cart.reduce((s,x)=>s+x.price*x.qty,0).toLocaleString()}
function openCart(){document.getElementById('cart-drawer')?.classList.add('open');document.getElementById('cart-backdrop')?.classList.add('open');renderCart()}
function closeCart(){document.getElementById('cart-drawer')?.classList.remove('open');document.getElementById('cart-backdrop')?.classList.remove('open')}
function checkout(){if(!cart.length){toast('Your cart is empty');return}toast('Checkout demo — connect your payment flow here')}
function toggleWish(btn){btn.classList.toggle('wished');btn.textContent=btn.classList.contains('wished')?'♥':'♡'}
function toast(text){const el=document.getElementById('toast');if(!el)return;el.textContent=text;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2200)}
function escapeHtml(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
function escapeAttr(s){return String(s).replace(/"/g,'&quot;')}
function subscribe(e){e.preventDefault();e.target.reset();toast('Welcome to the FitGear Club')}
function toggleMenu(){const nav=document.querySelector('.nav nav');if(!nav)return;nav.style.display=nav.style.display==='flex'?'none':'flex';nav.style.position='absolute';nav.style.top='72px';nav.style.left='0';nav.style.right='0';nav.style.padding='20px 5%';nav.style.background='#f7f8f3';nav.style.flexDirection='column';nav.style.borderBottom='1px solid #dfe4dd'}
document.addEventListener('click',e=>{const b=e.target.closest('.add-cart');if(!b)return;e.preventDefault();addToCart(b.dataset.id,b.dataset.name,Number(b.dataset.price),b.dataset.image||'')});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeCart()});
updateCartCount();renderCart();
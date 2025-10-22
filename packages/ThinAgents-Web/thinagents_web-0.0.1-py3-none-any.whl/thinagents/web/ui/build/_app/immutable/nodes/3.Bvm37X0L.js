import"../chunks/DsnmJJEf.js";import{aT as Rt,aG as F,$ as Tt,q as Vt,d as Ht,C as Dt,aU as Et,a1 as T,h as c,M as S,aV as ct,p as P,a0 as y,k as m,a as i,l as p,f as $,m as M,aW as tt,o as A,_ as E,aR as wt,aP as Lt,b as J,t as Z,aX as zt,s as U,n as X,a2 as Q,K as Ot}from"../chunks/Cim2JhJO.js";import{a as w,r as Nt,d as Ut,s as rt}from"../chunks/B1rQQ7sF.js";import{p as _,i as j,r as k,c as et,s as z,b as jt}from"../chunks/C7_YyfRN.js";import{C as Kt,D as qt,a as ut,c as Bt,w as kt,b as ft,d as V,e as L,m as vt,f as H,g as Wt,s as Gt,T as Yt,h as Ct,i as $t,j as Ft,P as Jt,R as Xt,I as gt,k as Qt,l as Zt,B as Pt}from"../chunks/DmkF1yUf.js";function te(a,t,r=t){var s=new WeakSet;Rt(a,"input",async e=>{var n=e?a.defaultValue:a.value;if(n=it(a)?dt(n):n,r(n),F!==null&&s.add(F),await Tt(),n!==(n=t())){var o=a.selectionStart,l=a.selectionEnd,f=a.value.length;if(a.value=n??"",l!==null){var d=a.value.length;o===l&&l===f&&d>f?(a.selectionStart=d,a.selectionEnd=d):(a.selectionStart=o,a.selectionEnd=Math.min(l,d))}}}),(Vt&&a.defaultValue!==a.value||Ht(t)==null&&a.value)&&(r(it(a)?dt(a.value):a.value),F!==null&&s.add(F)),Dt(()=>{var e=t();if(a===document.activeElement){var n=Et??F;if(s.has(n))return}it(a)&&e===dt(a.value)||a.type==="date"&&!e&&!a.value||e!==a.value&&(a.value=e??"")})}function it(a){var t=a.type;return t==="number"||t==="range"}function dt(a){return a===""?null:+a}const ht=Bt({component:"avatar",parts:["root","image","fallback"]}),mt=new Kt("Avatar.Root");class xt{static create(t){return mt.set(new xt(t))}opts;domContext;attachment;constructor(t){this.opts=t,this.domContext=new qt(this.opts.ref),this.loadImage=this.loadImage.bind(this),this.attachment=ut(this.opts.ref)}loadImage(t,r,s){if(this.opts.loadingStatus.current==="loaded")return;let e;const n=new Image;return n.src=t,r!==void 0&&(n.crossOrigin=r),s&&(n.referrerPolicy=s),this.opts.loadingStatus.current="loading",n.onload=()=>{e=this.domContext.setTimeout(()=>{this.opts.loadingStatus.current="loaded"},this.opts.delayMs.current)},n.onerror=()=>{this.opts.loadingStatus.current="error"},()=>{e&&this.domContext.clearTimeout(e)}}#t=T(()=>({id:this.opts.id.current,[ht.root]:"","data-status":this.opts.loadingStatus.current,...this.attachment}));get props(){return c(this.#t)}set props(t){S(this.#t,t)}}class _t{static create(t){return new _t(t,mt.get())}opts;root;attachment;constructor(t,r){this.opts=t,this.root=r,this.attachment=ut(this.opts.ref),kt.pre([()=>this.opts.src.current,()=>this.opts.crossOrigin.current],([s,e])=>{if(!s){this.root.opts.loadingStatus.current="error";return}this.root.loadImage(s,e,this.opts.referrerPolicy.current)})}#t=T(()=>({id:this.opts.id.current,style:{display:this.root.opts.loadingStatus.current==="loaded"?"block":"none"},"data-status":this.root.opts.loadingStatus.current,[ht.image]:"",src:this.opts.src.current,crossorigin:this.opts.crossOrigin.current,referrerpolicy:this.opts.referrerPolicy.current,...this.attachment}));get props(){return c(this.#t)}set props(t){S(this.#t,t)}}class yt{static create(t){return new yt(t,mt.get())}opts;root;attachment;constructor(t,r){this.opts=t,this.root=r,this.attachment=ut(this.opts.ref)}#t=T(()=>this.root.opts.loadingStatus.current==="loaded"?{display:"none"}:void 0);get style(){return c(this.#t)}set style(t){S(this.#t,t)}#e=T(()=>({style:this.style,"data-status":this.root.opts.loadingStatus.current,[ht.fallback]:"",...this.attachment}));get props(){return c(this.#e)}set props(t){S(this.#e,t)}}var ee=$("<div><!></div>");function ae(a,t){const r=ct();P(t,!0);let s=_(t,"delayMs",3,0),e=_(t,"loadingStatus",15,"loading"),n=_(t,"id",19,()=>ft(r)),o=_(t,"ref",15,null),l=k(t,["$$slots","$$events","$$legacy","delayMs","loadingStatus","onLoadingStatusChange","child","children","id","ref"]);const f=xt.create({delayMs:V(()=>s()),loadingStatus:V(()=>e(),u=>{e()!==u&&(e(u),t.onLoadingStatusChange?.(u))}),id:V(()=>n()),ref:V(()=>o(),u=>o(u))}),d=T(()=>vt(l,f.props));var v=y(),b=m(v);{var g=u=>{var h=y(),I=m(h);w(I,()=>t.child,()=>({props:c(d)})),i(u,h)},x=u=>{var h=ee();L(h,()=>({...c(d)}));var I=M(h);w(I,()=>t.children??tt),A(h),i(u,h)};j(b,u=>{t.child?u(g):u(x,!1)})}i(a,v),p()}var re=$("<img/>");function se(a,t){const r=ct();P(t,!0);let s=_(t,"id",19,()=>ft(r)),e=_(t,"ref",15,null),n=_(t,"crossorigin",3,void 0),o=_(t,"referrerpolicy",3,void 0),l=k(t,["$$slots","$$events","$$legacy","src","child","id","ref","crossorigin","referrerpolicy"]);const f=_t.create({src:V(()=>t.src),id:V(()=>s()),ref:V(()=>e(),u=>e(u)),crossOrigin:V(()=>n()),referrerPolicy:V(()=>o())}),d=T(()=>vt(l,f.props));var v=y(),b=m(v);{var g=u=>{var h=y(),I=m(h);w(I,()=>t.child,()=>({props:c(d)})),i(u,h)},x=u=>{var h=re();L(h,()=>({...c(d),src:t.src})),Nt(h),i(u,h)};j(b,u=>{t.child?u(g):u(x,!1)})}i(a,v),p()}var ne=$("<span><!></span>");function oe(a,t){const r=ct();P(t,!0);let s=_(t,"id",19,()=>ft(r)),e=_(t,"ref",15,null),n=k(t,["$$slots","$$events","$$legacy","children","child","id","ref"]);const o=yt.create({id:V(()=>s()),ref:V(()=>e(),g=>e(g))}),l=T(()=>vt(n,o.props));var f=y(),d=m(f);{var v=g=>{var x=y(),u=m(x);w(u,()=>t.child,()=>({props:c(l)})),i(g,x)},b=g=>{var x=ne();L(x,()=>({...c(l)}));var u=M(x);w(u,()=>t.children??tt),A(x),i(g,x)};j(d,g=>{t.child?g(v):g(b,!1)})}i(a,f),p()}function le(a,t){P(t,!0);let r=_(t,"ref",15,null),s=_(t,"loadingStatus",15,"loading"),e=k(t,["$$slots","$$events","$$legacy","ref","loadingStatus","class"]);var n=y(),o=m(n);{let l=T(()=>H("relative flex size-8 shrink-0 overflow-hidden rounded-full",t.class));et(o,()=>ae,(f,d)=>{d(f,z({"data-slot":"avatar",get class(){return c(l)}},()=>e,{get ref(){return r()},set ref(v){r(v)},get loadingStatus(){return s()},set loadingStatus(v){s(v)}}))})}i(a,n),p()}function ie(a,t){P(t,!0);let r=_(t,"ref",15,null),s=k(t,["$$slots","$$events","$$legacy","ref","class"]);var e=y(),n=m(e);{let o=T(()=>H("aspect-square size-full",t.class));et(n,()=>se,(l,f)=>{f(l,z({"data-slot":"avatar-image",get class(){return c(o)}},()=>s,{get ref(){return r()},set ref(d){r(d)}}))})}i(a,e),p()}function de(a,t){P(t,!0);let r=_(t,"ref",15,null),s=k(t,["$$slots","$$events","$$legacy","ref","class"]);var e=y(),n=m(e);{let o=T(()=>H("bg-muted flex size-full items-center justify-center rounded-full",t.class));et(n,()=>oe,(l,f)=>{f(l,z({"data-slot":"avatar-fallback",get class(){return c(o)}},()=>s,{get ref(){return r()},set ref(d){r(d)}}))})}i(a,e),p()}class ce{#t=E(!1);get isLoading(){return c(this.#t)}set isLoading(t){S(this.#t,t,!0)}#e=E("");get value(){return c(this.#e)}set value(t){S(this.#e,t,!0)}#a=E(240);get maxHeight(){return c(this.#a)}set maxHeight(t){S(this.#a,t,!0)}#r=E(void 0);get onSubmit(){return c(this.#r)}set onSubmit(t){S(this.#r,t,!0)}#s=E(!1);get disabled(){return c(this.#s)}set disabled(t){S(this.#s,t,!0)}#n=E(null);get textareaRef(){return c(this.#n)}set textareaRef(t){S(this.#n,t,!0)}#o=E(void 0);get onValueChange(){return c(this.#o)}set onValueChange(t){S(this.#o,t,!0)}constructor(t){this.isLoading=t.isLoading??!1,this.value=t.value??"",this.maxHeight=t.maxHeight??240,this.onSubmit=t.onSubmit,this.disabled=t.disabled??!1,this.onValueChange=t.onValueChange}setValue(t){this.value=t,this.onValueChange?.(t)}}const It=Symbol("prompt-input");function ue(a){wt(It,a)}function At(){const a=Lt(It);if(!a)throw new Error("PromptInput components must be used within PromptInput");return a}function fe(a,t){a.key==="Enter"&&(a.preventDefault(),t())}var ve=$('<div role="button" tabindex="-1"><!></div>');function ge(a,t){P(t,!0);let r=_(t,"isLoading",3,!1),s=_(t,"maxHeight",3,240);const e=new ce({isLoading:r(),value:t.value,onValueChange:t.onValueChange,maxHeight:s(),onSubmit:t.onSubmit,disabled:r()});ue(e),J(()=>{e.isLoading=r(),e.disabled=r()}),J(()=>{t.value!==void 0&&(e.value=t.value)}),J(()=>{e.onValueChange=t.onValueChange}),J(()=>{e.maxHeight=s()}),J(()=>{e.onSubmit=t.onSubmit});function n(){e.textareaRef?.focus()}var o=y(),l=m(o);et(l,()=>Yt,(f,d)=>{d(f,{children:(v,b)=>{var g=ve();g.__click=n,g.__keydown=[fe,n];var x=M(g);w(x,()=>t.children),A(g),Z(u=>Gt(g,1,u),[()=>Wt(H("border-input bg-background cursor-text rounded-3xl border p-2 shadow-xs",t.class))]),i(v,g)},$$slots:{default:!0}})}),i(a,o),p()}Ut(["click","keydown"]);var he=$("<textarea></textarea>");function me(a,t){P(t,!0);let r=_(t,"ref",15,null),s=_(t,"value",15),e=_(t,"data-slot",3,"textarea"),n=k(t,["$$slots","$$events","$$legacy","ref","value","class","data-slot"]);var o=he();zt(o),L(o,l=>({"data-slot":e(),class:l,...n}),[()=>H("border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive dark:bg-input/30 field-sizing-content shadow-xs flex min-h-16 w-full rounded-md border bg-transparent px-3 py-2 text-base outline-none transition-[color,box-shadow] focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",t.class)]),jt(o,l=>r(l),()=>r()),te(o,s),i(a,o),p()}function xe(a,t){P(t,!0);let r=_(t,"disableAutosize",3,!1),s=k(t,["$$slots","$$events","$$legacy","class","onkeydown","disableAutosize"]);const e=At();kt([()=>e.value,()=>e.maxHeight,()=>r()],()=>{r()||e.textareaRef&&(e.textareaRef.scrollTop===0&&(e.textareaRef.style.height="auto"),e.textareaRef.style.height=typeof e.maxHeight=="number"?`${Math.min(e.textareaRef.scrollHeight,e.maxHeight)}px`:`min(${e.textareaRef.scrollHeight}px, ${e.maxHeight})`)});function n(l){l.key==="Enter"&&!l.shiftKey&&(l.preventDefault(),e.onSubmit?.()),t.onkeydown?.(l)}function o(l){e.setValue(l.currentTarget.value)}{let l=T(()=>H("text-primary min-h-[44px] w-full resize-none border-none bg-transparent! shadow-none outline-none focus-visible:ring-0 focus-visible:ring-offset-0",t.class));me(a,z({get value(){return e.value},oninput:o,onkeydown:n,get class(){return c(l)},rows:1,get disabled(){return e.disabled}},()=>s,{get ref(){return e.textareaRef},set ref(f){e.textareaRef=f}}))}p()}var _e=$("<div><!></div>");function ye(a,t){P(t,!0);let r=k(t,["$$slots","$$events","$$legacy","class","children"]);var s=_e();L(s,n=>({class:n,...r}),[()=>H("flex items-center gap-2",t.class)]);var e=M(s);w(e,()=>t.children),A(s),i(a,s),p()}var be=$("<!> <!>",1);function Pe(a,t){P(t,!0);let r=_(t,"side",3,"top"),s=k(t,["$$slots","$$events","$$legacy","tooltip","children","class","side"]);const e=At();function n(f){f.stopPropagation()}var o=y(),l=m(o);et(l,()=>Ft,(f,d)=>{d(f,z(()=>s,{delayDuration:0,children:(v,b)=>{var g=be(),x=m(g);Ct(x,{get disabled(){return e.disabled},onclick:n,children:(h,I)=>{var C=y(),R=m(C);w(R,()=>t.children),i(h,C)},$$slots:{default:!0}});var u=U(x,2);$t(u,{get side(){return r()},get class(){return t.class},children:(h,I)=>{var C=y(),R=m(C);w(R,()=>t.tooltip),i(h,C)},$$slots:{default:!0}}),i(v,g)},$$slots:{default:!0}}))}),i(a,o),p()}class pe{constructor(t){}}const Se=Symbol("message");function we(a){wt(Se,a)}var ke=$("<div><!></div>");function pt(a,t){P(t,!0);let r=k(t,["$$slots","$$events","$$legacy","class","children"]);const s=new pe;we(s);var e=ke();L(e,o=>({class:o,...r}),[()=>H("flex gap-3",t.class)]);var n=M(e);w(n,()=>t.children),A(e),i(a,e),p()}var Ce=$("<!> <!>",1);function $e(a,t){P(t,!0);{let r=T(()=>H("h-8 w-8 shrink-0",t.class));le(a,{get class(){return c(r)},children:(s,e)=>{var n=Ce(),o=m(n);ie(o,{get src(){return t.src},get alt(){return t.alt}});var l=U(o,2);{var f=d=>{de(d,{children:(v,b)=>{X();var g=Q();Z(()=>rt(g,t.fallback)),i(v,g)},$$slots:{default:!0}})};j(l,d=>{t.fallback&&d(f)})}i(s,n)},$$slots:{default:!0}})}p()}var Ie=$("<div><!></div>"),Ae=$("<div><!></div>");function St(a,t){P(t,!0);let r=_(t,"markdown",3,!1),s=k(t,["$$slots","$$events","$$legacy","markdown","class","children"]);const e=H("rounded-lg p-2 text-foreground bg-secondary prose break-words whitespace-normal",t.class);var n=y(),o=m(n);{var l=d=>{var v=Ie();L(v,()=>({class:e,...s}));var b=M(v);w(b,()=>t.children),A(v),i(d,v)},f=d=>{var v=Ae();L(v,()=>({class:e,...s}));var b=M(v);w(b,()=>t.children),A(v),i(d,v)};j(o,d=>{r()?d(l):d(f,!1)})}i(a,n),p()}var Me=$("<div><!></div>");function Re(a,t){P(t,!0);let r=k(t,["$$slots","$$events","$$legacy","class","children"]);var s=Me();L(s,n=>({class:n,...r}),[()=>H("text-muted-foreground flex items-center gap-2",t.class)]);var e=M(s);w(e,()=>t.children),A(s),i(a,s),p()}var Te=$("<!> <!>",1);function Ve(a,t){let r=_(t,"side",3,"top"),s=k(t,["$$slots","$$events","$$legacy","tooltip","side","class","children"]);Jt(a,{children:(e,n)=>{Xt(e,z(()=>s,{children:(o,l)=>{var f=Te(),d=m(f);Ct(d,{children:(b,g)=>{var x=y(),u=m(x);w(u,()=>t.children),i(b,x)},$$slots:{default:!0}});var v=U(d,2);$t(v,{get side(){return r()},get class(){return t.class},children:(b,g)=>{var x=y(),u=m(x);w(u,()=>t.tooltip),i(b,x)},$$slots:{default:!0}}),i(o,f)},$$slots:{default:!0}}))},$$slots:{default:!0}})}function He(a,t){P(t,!0);/**
 * @license @lucide/svelte v0.544.0 - ISC
 *
 * ISC License
 *
 * Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2023 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2025.
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 * ---
 *
 * The MIT License (MIT) (for portions derived from Feather)
 *
 * Copyright (c) 2013-2023 Cole Bemis
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 */let r=k(t,["$$slots","$$events","$$legacy"]);const s=[["path",{d:"m5 12 7-7 7 7"}],["path",{d:"M12 19V5"}]];gt(a,z({name:"arrow-up"},()=>r,{get iconNode(){return s},children:(e,n)=>{var o=y(),l=m(o);w(l,()=>t.children??tt),i(e,o)},$$slots:{default:!0}})),p()}function De(a,t){P(t,!0);/**
 * @license @lucide/svelte v0.544.0 - ISC
 *
 * ISC License
 *
 * Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2023 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2025.
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 * ---
 *
 * The MIT License (MIT) (for portions derived from Feather)
 *
 * Copyright (c) 2013-2023 Cole Bemis
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 */let r=k(t,["$$slots","$$events","$$legacy"]);const s=[["rect",{width:"14",height:"14",x:"8",y:"8",rx:"2",ry:"2"}],["path",{d:"M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"}]];gt(a,z({name:"copy"},()=>r,{get iconNode(){return s},children:(e,n)=>{var o=y(),l=m(o);w(l,()=>t.children??tt),i(e,o)},$$slots:{default:!0}})),p()}function Ee(a,t){P(t,!0);/**
 * @license @lucide/svelte v0.544.0 - ISC
 *
 * ISC License
 *
 * Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2023 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2025.
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 * ---
 *
 * The MIT License (MIT) (for portions derived from Feather)
 *
 * Copyright (c) 2013-2023 Cole Bemis
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 */let r=k(t,["$$slots","$$events","$$legacy"]);const s=[["rect",{width:"18",height:"18",x:"3",y:"3",rx:"2"}]];gt(a,z({name:"square"},()=>r,{get iconNode(){return s},children:(e,n)=>{var o=y(),l=m(o);w(l,()=>t.children??tt),i(e,o)},$$slots:{default:!0}})),p()}var Le=$('<!> <div class="flex flex-col gap-2"><!> <!></div>',1),ze=$("<!> <!>",1),Oe=$('<div class="flex flex-1 flex-col"><div class="flex-1 overflow-y-auto p-4"><div class="mx-auto max-w-4xl"><div class="flex flex-col gap-8"></div></div></div> <div class="p-4"><div class="mx-auto max-w-4xl"><!></div></div></div>');function We(a,t){P(t,!0);let r=E(""),s=E(!1),e=E(Ot([]));async function n(){if(!c(r).trim())return;S(s,!0);const h={id:crypto.randomUUID(),content:c(r),timestamp:new Date().toISOString(),type:"user"};S(e,[...c(e),h],!0);const I=c(r);S(r,"");try{const C=await fetch("/api/agent/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({input:I})});if(!C.ok)throw new Error("Failed to get response");const R=await C.json(),q={id:crypto.randomUUID(),content:R.content,timestamp:R.timestamp||new Date().toISOString(),type:"assistant"};S(e,[...c(e),q],!0)}catch(C){console.error("Error:",C);const R={id:crypto.randomUUID(),content:"Sorry, there was an error processing your request.",timestamp:new Date().toISOString(),type:"assistant"};S(e,[...c(e),R],!0)}finally{S(s,!1)}}function o(h){S(r,h,!0)}function l(h){navigator.clipboard.writeText(h)}var f=Oe(),d=M(f),v=M(d),b=M(v);Qt(b,21,()=>c(e),Zt,(h,I)=>{var C=y(),R=m(C);{var q=N=>{pt(N,{class:"justify-end",children:(at,B)=>{St(at,{children:(O,W)=>{X();var K=Q();Z(()=>rt(K,c(I).content)),i(O,K)},$$slots:{default:!0}})},$$slots:{default:!0}})},st=N=>{pt(N,{class:"justify-start",children:(at,B)=>{var O=Le(),W=m(O);$e(W,{src:"/avatars/ai.png",alt:"AI",fallback:"AI"});var K=U(W,2),G=M(K);St(G,{class:"bg-transparent p-0",children:(Y,ot)=>{X();var D=Q();Z(()=>rt(D,c(I).content)),i(Y,D)},$$slots:{default:!0}});var nt=U(G,2);Re(nt,{children:(Y,ot)=>{Ve(Y,{tooltip:lt=>{X();var bt=Q("Copy");i(lt,bt)},children:(lt,bt)=>{Pt(lt,{variant:"ghost",size:"icon",class:"h-8 w-8",onclick:()=>l(c(I).content),children:(Mt,Ne)=>{De(Mt,{class:"h-4 w-4"})},$$slots:{default:!0}})},$$slots:{tooltip:!0,default:!0}})},$$slots:{default:!0}}),A(K),i(at,O)},$$slots:{default:!0}})};j(R,N=>{c(I).type==="user"?N(q):N(st,!1)})}i(h,C)}),A(b),A(v),A(d);var g=U(d,2),x=M(g),u=M(x);ge(u,{get value(){return c(r)},onValueChange:o,get isLoading(){return c(s)},onSubmit:n,class:"w-full",children:(h,I)=>{var C=ze(),R=m(C);xe(R,{placeholder:"Ask me anything..."});var q=U(R,2);ye(q,{class:"justify-end pt-2",children:(st,N)=>{Pe(st,{tooltip:B=>{X();var O=Q();Z(()=>rt(O,c(s)?"Stop generation":"Send message")),i(B,O)},children:(B,O)=>{Pt(B,{variant:"default",size:"icon",class:"h-8 w-8 rounded-full",onclick:n,children:(W,K)=>{var G=y(),nt=m(G);{var Y=D=>{Ee(D,{class:"size-5 fill-current"})},ot=D=>{He(D,{class:"size-5"})};j(nt,D=>{c(s)?D(Y):D(ot,!1)})}i(W,G)},$$slots:{default:!0}})},$$slots:{tooltip:!0,default:!0}})},$$slots:{default:!0}}),i(h,C)},$$slots:{default:!0}}),A(x),A(g),A(f),i(a,f),p()}export{We as component};

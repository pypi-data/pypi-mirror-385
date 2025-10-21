import"./CWj6FrbW.js";import{p as c,a as m,f as $,n as _,c as G,s as f,g,b as v,r as P}from"./C3xJX0nD.js";import{c as w,a as p,f as L}from"./CAPx0Bfm.js";import{s as S,r as y,p as x}from"./xQhUoIl9.js";import{a as V,s as j}from"./DmGM9V9Q.js";import{I as z,_ as k,a as q}from"./CWuDkrMZ.js";import{u as A}from"./BOmrKuMn.js";import{s as I}from"./DoEId1MK.js";function B(a,e){c(e,!0);/**
 * @license @lucide/svelte v0.482.0 - ISC
 *
 * ISC License
 *
 * Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2022.
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
 */let r=y(e,["$$slots","$$events","$$legacy"]);const s=[["rect",{width:"18",height:"18",x:"3",y:"3",rx:"2"}],["path",{d:"M3 9h18"}],["path",{d:"M3 15h18"}],["path",{d:"M9 3v18"}],["path",{d:"M15 3v18"}]];z(a,S({name:"grid-3x3"},()=>r,{get iconNode(){return s},children:(o,i)=>{var t=w(),n=$(t);I(n,()=>e.children??_),p(o,t)},$$slots:{default:!0}})),m()}function D(a,e){c(e,!0);/**
 * @license @lucide/svelte v0.482.0 - ISC
 *
 * ISC License
 *
 * Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2022.
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
 */let r=y(e,["$$slots","$$events","$$legacy"]);const s=[["rect",{width:"18",height:"18",x:"3",y:"3",rx:"2",ry:"2"}],["circle",{cx:"9",cy:"9",r:"2"}],["path",{d:"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"}]];z(a,S({name:"image"},()=>r,{get iconNode(){return s},children:(o,i)=>{var t=w(),n=$(t);I(n,()=>e.children??_),p(o,t)},$$slots:{default:!0}})),m()}var E=L('<div class="w-300 flex space-x-4 text-diffuse-foreground"><!> <!> <!></div>');function U(a,e){c(e,!0);const r=()=>j(n,"$sampleSize",s),[s,o]=V(),i=x(e,"min",3,100),t=x(e,"max",3,1500),{sampleSize:n,updateSampleSize:M}=A(),N=v(()=>r().width),b=k.throttle(d=>{M(d[0])},100);var l=E(),h=G(l);B(h,{class:"h-6 w-6"});var u=f(h,2);{let d=v(()=>[g(N)]);q(u,{class:"w-full flex-1",get value(){return g(d)},get min(){return i()},get max(){return t()},step:1,get onValueChange(){return b}})}var C=f(u,2);D(C,{class:"h-6 w-6"}),P(l),p(a,l),m(),o()}export{U as I,D as a};

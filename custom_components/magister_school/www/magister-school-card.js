/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const e=window,t=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=Symbol(),s=new WeakMap;let a=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const i=this.t;if(t&&void 0===e){const t=void 0!==i&&1===i.length;t&&(e=s.get(i)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),t&&s.set(i,e))}return e}toString(){return this.cssText}};const r=(e,...t)=>{const s=1===e.length?e[0]:t.reduce((t,i,s)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[s+1],e[0]);return new a(s,e,i)},n=t?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return(e=>new a("string"==typeof e?e:e+"",void 0,i))(t)})(e):e;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */var o;const d=window,l=d.trustedTypes,c=l?l.emptyScript:"",h=d.reactiveElementPolyfillSupport,g={toAttribute(e,t){switch(t){case Boolean:e=e?c:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=null!==e;break;case Number:i=null===e?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch(e){i=null}}return i}},p=(e,t)=>t!==e&&(t==t||e==e),v={attribute:!0,type:String,converter:g,reflect:!1,hasChanged:p},u="finalized";let m=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(e){var t;this.finalize(),(null!==(t=this.h)&&void 0!==t?t:this.h=[]).push(e)}static get observedAttributes(){this.finalize();const e=[];return this.elementProperties.forEach((t,i)=>{const s=this._$Ep(i,t);void 0!==s&&(this._$Ev.set(s,i),e.push(s))}),e}static createProperty(e,t=v){if(t.state&&(t.attribute=!1),this.finalize(),this.elementProperties.set(e,t),!t.noAccessor&&!this.prototype.hasOwnProperty(e)){const i="symbol"==typeof e?Symbol():"__"+e,s=this.getPropertyDescriptor(e,i,t);void 0!==s&&Object.defineProperty(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){return{get(){return this[t]},set(s){const a=this[e];this[t]=s,this.requestUpdate(e,a,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)||v}static finalize(){if(this.hasOwnProperty(u))return!1;this[u]=!0;const e=Object.getPrototypeOf(this);if(e.finalize(),void 0!==e.h&&(this.h=[...e.h]),this.elementProperties=new Map(e.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const e=this.properties,t=[...Object.getOwnPropertyNames(e),...Object.getOwnPropertySymbols(e)];for(const i of t)this.createProperty(i,e[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const e of i)t.unshift(n(e))}else void 0!==e&&t.push(n(e));return t}static _$Ep(e,t){const i=t.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof e?e.toLowerCase():void 0}_$Eu(){var e;this._$E_=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(e=this.constructor.h)||void 0===e||e.forEach(e=>e(this))}addController(e){var t,i;(null!==(t=this._$ES)&&void 0!==t?t:this._$ES=[]).push(e),void 0!==this.renderRoot&&this.isConnected&&(null===(i=e.hostConnected)||void 0===i||i.call(e))}removeController(e){var t;null===(t=this._$ES)||void 0===t||t.splice(this._$ES.indexOf(e)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((e,t)=>{this.hasOwnProperty(t)&&(this._$Ei.set(t,this[t]),delete this[t])})}createRenderRoot(){var i;const s=null!==(i=this.shadowRoot)&&void 0!==i?i:this.attachShadow(this.constructor.shadowRootOptions);return((i,s)=>{t?i.adoptedStyleSheets=s.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet):s.forEach(t=>{const s=document.createElement("style"),a=e.litNonce;void 0!==a&&s.setAttribute("nonce",a),s.textContent=t.cssText,i.appendChild(s)})})(s,this.constructor.elementStyles),s}connectedCallback(){var e;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(e=this._$ES)||void 0===e||e.forEach(e=>{var t;return null===(t=e.hostConnected)||void 0===t?void 0:t.call(e)})}enableUpdating(e){}disconnectedCallback(){var e;null===(e=this._$ES)||void 0===e||e.forEach(e=>{var t;return null===(t=e.hostDisconnected)||void 0===t?void 0:t.call(e)})}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$EO(e,t,i=v){var s;const a=this.constructor._$Ep(e,i);if(void 0!==a&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:g).toAttribute(t,i.type);this._$El=e,null==r?this.removeAttribute(a):this.setAttribute(a,r),this._$El=null}}_$AK(e,t){var i;const s=this.constructor,a=s._$Ev.get(e);if(void 0!==a&&this._$El!==a){const e=s.getPropertyOptions(a),r="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==(null===(i=e.converter)||void 0===i?void 0:i.fromAttribute)?e.converter:g;this._$El=a,this[a]=r.fromAttribute(t,e.type),this._$El=null}}requestUpdate(e,t,i){let s=!0;void 0!==e&&(((i=i||this.constructor.getPropertyOptions(e)).hasChanged||p)(this[e],t)?(this._$AL.has(e)||this._$AL.set(e,t),!0===i.reflect&&this._$El!==e&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(e,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var e;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((e,t)=>this[t]=e),this._$Ei=void 0);let t=!1;const i=this._$AL;try{t=this.shouldUpdate(i),t?(this.willUpdate(i),null===(e=this._$ES)||void 0===e||e.forEach(e=>{var t;return null===(t=e.hostUpdate)||void 0===t?void 0:t.call(e)}),this.update(i)):this._$Ek()}catch(e){throw t=!1,this._$Ek(),e}t&&this._$AE(i)}willUpdate(e){}_$AE(e){var t;null===(t=this._$ES)||void 0===t||t.forEach(e=>{var t;return null===(t=e.hostUpdated)||void 0===t?void 0:t.call(e)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(e){return!0}update(e){void 0!==this._$EC&&(this._$EC.forEach((e,t)=>this._$EO(t,this[t],e)),this._$EC=void 0),this._$Ek()}updated(e){}firstUpdated(e){}};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var _;m[u]=!0,m.elementProperties=new Map,m.elementStyles=[],m.shadowRootOptions={mode:"open"},null==h||h({ReactiveElement:m}),(null!==(o=d.reactiveElementVersions)&&void 0!==o?o:d.reactiveElementVersions=[]).push("1.6.3");const f=window,$=f.trustedTypes,w=$?$.createPolicy("lit-html",{createHTML:e=>e}):void 0,y="$lit$",b=`lit$${(Math.random()+"").slice(9)}$`,x="?"+b,k=`<${x}>`,A=document,j=()=>A.createComment(""),S=e=>null===e||"object"!=typeof e&&"function"!=typeof e,E=Array.isArray,C="[ \t\n\f\r]",W=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,z=/-->/g,R=/>/g,U=RegExp(`>|${C}(?:([^\\s"'>=/]+)(${C}*=${C}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),L=/'/g,H=/"/g,N=/^(?:script|style|textarea|title)$/i,O=(e=>(t,...i)=>({_$litType$:e,strings:t,values:i}))(1),P=Symbol.for("lit-noChange"),D=Symbol.for("lit-nothing"),T=new WeakMap,M=A.createTreeWalker(A,129,null,!1);function V(e,t){if(!Array.isArray(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==w?w.createHTML(t):t}const G=(e,t)=>{const i=e.length-1,s=[];let a,r=2===t?"<svg>":"",n=W;for(let t=0;t<i;t++){const i=e[t];let o,d,l=-1,c=0;for(;c<i.length&&(n.lastIndex=c,d=n.exec(i),null!==d);)c=n.lastIndex,n===W?"!--"===d[1]?n=z:void 0!==d[1]?n=R:void 0!==d[2]?(N.test(d[2])&&(a=RegExp("</"+d[2],"g")),n=U):void 0!==d[3]&&(n=U):n===U?">"===d[0]?(n=null!=a?a:W,l=-1):void 0===d[1]?l=-2:(l=n.lastIndex-d[2].length,o=d[1],n=void 0===d[3]?U:'"'===d[3]?H:L):n===H||n===L?n=U:n===z||n===R?n=W:(n=U,a=void 0);const h=n===U&&e[t+1].startsWith("/>")?" ":"";r+=n===W?i+k:l>=0?(s.push(o),i.slice(0,l)+y+i.slice(l)+b+h):i+b+(-2===l?(s.push(void 0),t):h)}return[V(e,r+(e[i]||"<?>")+(2===t?"</svg>":"")),s]};class I{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let a=0,r=0;const n=e.length-1,o=this.parts,[d,l]=G(e,t);if(this.el=I.createElement(d,i),M.currentNode=this.el.content,2===t){const e=this.el.content,t=e.firstChild;t.remove(),e.append(...t.childNodes)}for(;null!==(s=M.nextNode())&&o.length<n;){if(1===s.nodeType){if(s.hasAttributes()){const e=[];for(const t of s.getAttributeNames())if(t.endsWith(y)||t.startsWith(b)){const i=l[r++];if(e.push(t),void 0!==i){const e=s.getAttribute(i.toLowerCase()+y).split(b),t=/([.?@])?(.*)/.exec(i);o.push({type:1,index:a,name:t[2],strings:e,ctor:"."===t[1]?J:"?"===t[1]?Y:"@"===t[1]?Q:F})}else o.push({type:6,index:a})}for(const t of e)s.removeAttribute(t)}if(N.test(s.tagName)){const e=s.textContent.split(b),t=e.length-1;if(t>0){s.textContent=$?$.emptyScript:"";for(let i=0;i<t;i++)s.append(e[i],j()),M.nextNode(),o.push({type:2,index:++a});s.append(e[t],j())}}}else if(8===s.nodeType)if(s.data===x)o.push({type:2,index:a});else{let e=-1;for(;-1!==(e=s.data.indexOf(b,e+1));)o.push({type:7,index:a}),e+=b.length-1}a++}}static createElement(e,t){const i=A.createElement("template");return i.innerHTML=e,i}}function B(e,t,i=e,s){var a,r,n,o;if(t===P)return t;let d=void 0!==s?null===(a=i._$Co)||void 0===a?void 0:a[s]:i._$Cl;const l=S(t)?void 0:t._$litDirective$;return(null==d?void 0:d.constructor)!==l&&(null===(r=null==d?void 0:d._$AO)||void 0===r||r.call(d,!1),void 0===l?d=void 0:(d=new l(e),d._$AT(e,i,s)),void 0!==s?(null!==(n=(o=i)._$Co)&&void 0!==n?n:o._$Co=[])[s]=d:i._$Cl=d),void 0!==d&&(t=B(e,d._$AS(e,t.values),d,s)),t}class K{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){var t;const{el:{content:i},parts:s}=this._$AD,a=(null!==(t=null==e?void 0:e.creationScope)&&void 0!==t?t:A).importNode(i,!0);M.currentNode=a;let r=M.nextNode(),n=0,o=0,d=s[0];for(;void 0!==d;){if(n===d.index){let t;2===d.type?t=new q(r,r.nextSibling,this,e):1===d.type?t=new d.ctor(r,d.name,d.strings,this,e):6===d.type&&(t=new X(r,this,e)),this._$AV.push(t),d=s[++o]}n!==(null==d?void 0:d.index)&&(r=M.nextNode(),n++)}return M.currentNode=A,a}v(e){let t=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class q{constructor(e,t,i,s){var a;this.type=2,this._$AH=D,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cp=null===(a=null==s?void 0:s.isConnected)||void 0===a||a}get _$AU(){var e,t;return null!==(t=null===(e=this._$AM)||void 0===e?void 0:e._$AU)&&void 0!==t?t:this._$Cp}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===(null==e?void 0:e.nodeType)&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=B(this,e,t),S(e)?e===D||null==e||""===e?(this._$AH!==D&&this._$AR(),this._$AH=D):e!==this._$AH&&e!==P&&this._(e):void 0!==e._$litType$?this.g(e):void 0!==e.nodeType?this.$(e):(e=>E(e)||"function"==typeof(null==e?void 0:e[Symbol.iterator]))(e)?this.T(e):this._(e)}k(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}$(e){this._$AH!==e&&(this._$AR(),this._$AH=this.k(e))}_(e){this._$AH!==D&&S(this._$AH)?this._$AA.nextSibling.data=e:this.$(A.createTextNode(e)),this._$AH=e}g(e){var t;const{values:i,_$litType$:s}=e,a="number"==typeof s?this._$AC(e):(void 0===s.el&&(s.el=I.createElement(V(s.h,s.h[0]),this.options)),s);if((null===(t=this._$AH)||void 0===t?void 0:t._$AD)===a)this._$AH.v(i);else{const e=new K(a,this),t=e.u(this.options);e.v(i),this.$(t),this._$AH=e}}_$AC(e){let t=T.get(e.strings);return void 0===t&&T.set(e.strings,t=new I(e)),t}T(e){E(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,s=0;for(const a of e)s===t.length?t.push(i=new q(this.k(j()),this.k(j()),this,this.options)):i=t[s],i._$AI(a),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,t);e&&e!==this._$AB;){const t=e.nextSibling;e.remove(),e=t}}setConnected(e){var t;void 0===this._$AM&&(this._$Cp=e,null===(t=this._$AP)||void 0===t||t.call(this,e))}}class F{constructor(e,t,i,s,a){this.type=1,this._$AH=D,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=a,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=D}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(e,t=this,i,s){const a=this.strings;let r=!1;if(void 0===a)e=B(this,e,t,0),r=!S(e)||e!==this._$AH&&e!==P,r&&(this._$AH=e);else{const s=e;let n,o;for(e=a[0],n=0;n<a.length-1;n++)o=B(this,s[i+n],t,n),o===P&&(o=this._$AH[n]),r||(r=!S(o)||o!==this._$AH[n]),o===D?e=D:e!==D&&(e+=(null!=o?o:"")+a[n+1]),this._$AH[n]=o}r&&!s&&this.j(e)}j(e){e===D?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=e?e:"")}}class J extends F{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===D?void 0:e}}const Z=$?$.emptyScript:"";class Y extends F{constructor(){super(...arguments),this.type=4}j(e){e&&e!==D?this.element.setAttribute(this.name,Z):this.element.removeAttribute(this.name)}}class Q extends F{constructor(e,t,i,s,a){super(e,t,i,s,a),this.type=5}_$AI(e,t=this){var i;if((e=null!==(i=B(this,e,t,0))&&void 0!==i?i:D)===P)return;const s=this._$AH,a=e===D&&s!==D||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,r=e!==D&&(s===D||a);a&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){var t,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(t=this.options)||void 0===t?void 0:t.host)&&void 0!==i?i:this.element,e):this._$AH.handleEvent(e)}}class X{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){B(this,e)}}const ee=f.litHtmlPolyfillSupport;null==ee||ee(I,q),(null!==(_=f.litHtmlVersions)&&void 0!==_?_:f.litHtmlVersions=[]).push("2.8.0");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var te,ie;class se extends m{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var e,t;const i=super.createRenderRoot();return null!==(e=(t=this.renderOptions).renderBefore)&&void 0!==e||(t.renderBefore=i.firstChild),i}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,i)=>{var s,a;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:t;let n=r._$litPart$;if(void 0===n){const e=null!==(a=null==i?void 0:i.renderBefore)&&void 0!==a?a:null;r._$litPart$=n=new q(t.insertBefore(j(),e),e,void 0,null!=i?i:{})}return n._$AI(e),n})(t,this.renderRoot,this.renderOptions)}connectedCallback(){var e;super.connectedCallback(),null===(e=this._$Do)||void 0===e||e.setConnected(!0)}disconnectedCallback(){var e;super.disconnectedCallback(),null===(e=this._$Do)||void 0===e||e.setConnected(!1)}render(){return P}}se.finalized=!0,se._$litElement$=!0,null===(te=globalThis.litElementHydrateSupport)||void 0===te||te.call(globalThis,{LitElement:se});const ae=globalThis.litElementPolyfillSupport;null==ae||ae({LitElement:se}),(null!==(ie=globalThis.litElementVersions)&&void 0!==ie?ie:globalThis.litElementVersions=[]).push("3.3.3");class re extends se{static properties={hass:{},config:{},_data:{state:!0},_kindNaam:{state:!0}};static styles=r`
    :host {
      display: block;
      width: 100%;
    }
    
    .card {
      padding: 20px;
      background: var(--card-background-color);
      border-radius: var(--ha-card-border-radius, 12px);
      box-shadow: var(--ha-card-box-shadow, 0px 2px 4px rgba(0,0,0,0.1));
      width: 100%;
      box-sizing: border-box;
    }
    
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 16px;
    }
    
    .header h1 {
      margin: 0;
      font-size: 1.8em;
      color: var(--primary-text-color);
      flex-grow: 1;
    }
    
    .kind-info {
      background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
      color: white;
      padding: 12px 20px;
      border-radius: 10px;
      margin-bottom: 20px;
    }
    
    .kind-info h2 {
      margin: 0;
      font-size: 1.4em;
    }
    
    .kind-meta {
      display: flex;
      gap: 16px;
      margin-top: 8px;
      font-size: 0.9em;
      opacity: 0.9;
    }
    
    .layout-selector {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    
    .layout-btn {
      padding: 10px 16px;
      border: 1px solid var(--primary-color);
      background: transparent;
      color: var(--primary-color);
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.9em;
      transition: all 0.3s ease;
    }
    
    .layout-btn:hover {
      background: var(--primary-color);
      color: white;
      transform: translateY(-2px);
    }
    
    .layout-btn.active {
      background: var(--primary-color);
      color: white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Responsive Grid Layouts */
    .grid-1 { 
      display: grid; 
      grid-template-columns: 1fr; 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-2 { 
      display: grid; 
      grid-template-columns: repeat(2, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-3 { 
      display: grid; 
      grid-template-columns: repeat(3, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-4 { 
      display: grid; 
      grid-template-columns: repeat(4, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-5 { 
      display: grid; 
      grid-template-columns: repeat(5, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-6 { 
      display: grid; 
      grid-template-columns: repeat(6, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-auto { 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
      gap: 20px; 
      width: 100%;
    }

    /* Custom Column Layout */
    .column-container {
      display: flex;
      gap: 20px;
      width: 100%;
    }

    .column {
      display: flex;
      flex-direction: column;
      gap: 20px;
      flex: 1;
      min-width: 0;
    }

    @media (max-width: 1200px) {
      .column-container {
        flex-wrap: wrap;
      }
      
      .column {
        flex: 1 1 calc(50% - 10px);
        min-width: 300px;
      }
    }

    @media (max-width: 768px) {
      .column-container {
        flex-direction: column;
      }
      
      .column {
        flex: 1 1 100%;
        min-width: 100%;
      }
    }
    
    @media (max-width: 1200px) {
      .grid-3 {
        grid-template-columns: repeat(2, 1fr);
      }
      
      .grid-4,
      .grid-5,
      .grid-6 {
        grid-template-columns: repeat(3, 1fr);
      }
    }
    
    @media (max-width: 768px) {
      .card {
        padding: 16px;
      }
      
      .header {
        flex-direction: column;
        align-items: flex-start;
      }
      
      .header h1 {
        font-size: 1.5em;
      }
      
      .layout-selector {
        width: 100%;
        justify-content: center;
      }
      
      .grid-2,
      .grid-3,
      .grid-4,
      .grid-5,
      .grid-6 {
        grid-template-columns: 1fr;
      }
      
      .grid-auto {
        grid-template-columns: 1fr;
      }
      
      .kind-meta {
        flex-direction: column;
        gap: 4px;
      }
    }
    
    @media (max-width: 480px) {
      .card {
        padding: 12px;
      }
      
      .layout-btn {
        padding: 8px 12px;
        font-size: 0.8em;
      }
    }
    
    /* Widget Styling */
    .widget {
      background: var(--secondary-background-color);
      border-radius: 12px;
      padding: 20px;
      border-left: 6px solid var(--primary-color);
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      height: fit-content;
      min-height: 200px;
      display: flex;
      flex-direction: column;
    }
    
    .widget:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .widget-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--divider-color);
    }
    
    .widget-title {
      font-size: 1.3em;
      font-weight: bold;
      color: var(--primary-text-color);
      margin: 0;
    }
    
    .widget-icon {
      font-size: 1.4em;
      background: var(--primary-color);
      color: white;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
    }
    
    .widget-content {
      flex-grow: 1;
      overflow-y: auto;
      max-height: 400px;
    }
    
    /* Specifieke Widget Styles */
    .cijfer-item, .afspraak-item, .opdracht-item, .mededeling-item {
      padding: 12px;
      border-left: 4px solid var(--accent-color);
      margin-bottom: 12px;
      background: var(--primary-background-color);
      border-radius: 8px;
      transition: background-color 0.2s ease;
    }
    
    .cijfer-item:hover, .afspraak-item:hover, .opdracht-item:hover {
      background: var(--secondary-background-color);
    }

    /* Uitval styling */
    .afspraak-item.uitval {
      border-left-color: var(--error-color, #f44336);
      background: rgba(244, 67, 54, 0.08);
      opacity: 0.85;
      position: relative;
    }

    .afspraak-item.uitval .uitval-label {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: var(--error-color, #f44336);
      color: white;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 0.78em;
      font-weight: bold;
      margin-bottom: 4px;
      letter-spacing: 0.04em;
    }

    .afspraak-item.uitval .les-tijd,
    .afspraak-item.uitval .les-omschrijving {
      text-decoration: line-through;
      opacity: 0.6;
    }

    /* Gewijzigd styling */
    .afspraak-item.gewijzigd {
      border-left-color: var(--warning-color, #ff9800);
      background: rgba(255, 152, 0, 0.08);
      position: relative;
    }

    .afspraak-item.gewijzigd .uitval-label {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: var(--warning-color, #ff9800);
      color: white;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 0.78em;
      font-weight: bold;
      margin-bottom: 4px;
      letter-spacing: 0.04em;
    }
    
    .vak { 
      font-weight: bold; 
      font-size: 1.1em;
    }
    
    .waarde { 
      font-size: 1.3em; 
      color: var(--accent-color);
      font-weight: bold;
    }
    
    .cijfer-item .wf {
      font-size: 0.85em;
      opacity: 0.75;
      margin-left: 4px;
    }
    
    .tijd { 
      font-size: 0.9em; 
      color: var(--secondary-text-color);
      margin-top: 4px;
    }
    
    .empty-state {
      text-align: center;
      color: var(--secondary-text-color);
      font-style: italic;
      padding: 40px 20px;
      font-size: 1.1em;
    }
    
    /* Scrollbar styling */
    .widget-content::-webkit-scrollbar {
      width: 6px;
    }
    
    .widget-content::-webkit-scrollbar-track {
      background: var(--secondary-background-color);
      border-radius: 3px;
    }
    
    .widget-content::-webkit-scrollbar-thumb {
      background: var(--primary-color);
      border-radius: 3px;
    }
    
    .widget-content::-webkit-scrollbar-thumb:hover {
      background: var(--accent-color);
    }
    
    /* Badge voor belangrijke items */
    .badge {
      background: var(--error-color);
      color: white;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.8em;
      margin-left: 8px;
    }
    
    .badge-warning {
      background: var(--warning-color);
    }
    
    .badge-success {
      background: var(--success-color);
    }

    .schoolweek-row {
      display: grid;
      grid-template-columns: minmax(90px, 1fr) minmax(120px, 1fr);
      gap: 12px;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid var(--divider-color);
    }

    .schoolweek-row:last-child {
      border-bottom: 0;
    }

    .schoolweek-day {
      color: var(--primary-text-color);
      font-weight: 600;
    }

    .schoolweek-time {
      color: var(--secondary-text-color);
      text-align: right;
    }
  `;constructor(){super(),this._data=null,this._kindNaam="",this._layout="grid-auto"}setConfig(e){this.config={layout:"auto",show_widgets:["stats","schooltijden","volgende_schooldag","rooster_vandaag","huiswerk","cijfers","voortgangscijfers","opdrachten"],widget_columns:null,hide_layout_selector:!1,hide_kind_info:!1,...e},this._layout=this._normalizeLayout(this.config.layout)}_normalizeLayout(e){if(!e||"auto"===e)return"grid-auto";return["grid-1","grid-2","grid-3","grid-4","grid-5","grid-6","grid-auto"].includes(e)?e:"grid-auto"}connectedCallback(){super.connectedCallback(),this._fetchData()}_fetchData(){if(!this.hass)return;const e=this.hass.states[this.config.entity];e&&(this._data=e.attributes,this._extractKindInfo())}_extractKindInfo(){if(!this._data)return;const e=this.config.entity||"";this._kindNaam=this._data.naam||this._data.kind_naam||e.replace("sensor.magister_","").replace(/_/g," ")}_formatTijd(e){if(!e)return"";const t=e.replace(" ","T"),i=new Date(t);return isNaN(i.getTime())?e.substr(11,5):i.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",hour12:!1})}_getLocaleDateStr(e){return e?e.substr(0,10):""}_getVandaag(){return(new Date).toLocaleDateString("en-CA")}_getMorgen(){const e=new Date;return e.setDate(e.getDate()+1),e.toLocaleDateString("en-CA")}_setLayout(e){this._layout=e}render(){if(!this._data)return O`
        <div class="card">
          <div class="empty-state">📚 School data laden...</div>
        </div>
      `;const e=this.config.widget_columns&&Object.keys(this.config.widget_columns).length>0;return O`
      <div class="card">
        <div class="header">
          <h1>🏫 School Dashboard</h1>
          ${e||this.config.hide_layout_selector?"":O`
            <div class="layout-selector">
              <button class="layout-btn ${"grid-1"===this._layout?"active":""}" 
                      @click=${()=>this._setLayout("grid-1")}>1 Kolom</button>
              <button class="layout-btn ${"grid-2"===this._layout?"active":""}" 
                      @click=${()=>this._setLayout("grid-2")}>2 Kolommen</button>
              <button class="layout-btn ${"grid-3"===this._layout?"active":""}" 
                      @click=${()=>this._setLayout("grid-3")}>3 Kolommen</button>
              <button class="layout-btn ${"grid-auto"===this._layout?"active":""}" 
                      @click=${()=>this._setLayout("grid-auto")}>Auto Fit</button>
            </div>
          `}
        </div>
        
        ${this.config.hide_kind_info?"":this._renderKindInfo()}
        
        ${e?this._renderColumnLayout():O`
          <div class="${this._layout}">
            ${this._renderWidgets()}
          </div>
        `}
      </div>
    `}_renderKindInfo(){return this._kindNaam?O`
      <div class="kind-info">
        <h2>${this._kindNaam}</h2>
        <div class="kind-meta">
          ${this._data.stamnummer?O`<span>🎫 Stamnummer: ${this._data.stamnummer}</span>`:""}
          ${this._data.klas?O`<span>🏫 Klas: ${this._data.klas}</span>`:""}
          ${this._data.profiel?O`<span>🧭 Profiel: ${this._data.profiel}</span>`:""}
          ${this._data.geboortedatum?O`<span>🎂 Geboortedatum: ${this._data.geboortedatum}</span>`:""}
          <span>🕒 Laatste update: ${this.hass.states[this.config.entity].state}</span>
        </div>
      </div>
    `:O``}_renderColumnLayout(){const e=this.config.widget_columns,t=Object.keys(e).sort();return O`
      <div class="column-container">
        ${t.map(t=>O`
          <div class="column">
            ${this._renderWidgetsForColumn(e[t])}
          </div>
        `)}
      </div>
    `}_renderWidgetsForColumn(e){return e&&Array.isArray(e)?e.map(e=>this._getWidgetByName(e)).filter(e=>e):[]}_getWidgetByName(e){switch(e){case"stats":return this._renderStatsWidget();case"schooltijden":return this._renderSchooltijdenWidget();case"week_schooltijden":return this._renderWeekSchooltijdenWidget();case"volgende_schooldag":return this._renderVolgendeSchooldagWidget();case"volgende_les":return this._renderVolgendeLesWidget();case"rooster_vandaag":return this._renderRoosterWidget();case"rooster_meta":return this._renderRoosterMetaWidget();case"rooster_morgen":return this._renderRoosterMorgenWidget();case"huiswerk":return this._renderHuiswerkWidget();case"cijfers":return this._renderCijfersWidget();case"voortgangscijfers":return this._renderVoortgangscijfersWidget();case"opdrachten":return this._renderOpdrachtenWidget();case"absenties":return this._renderAbsentiesWidget();case"wijzigingen":return this._renderWijzigingenWidget();case"aanmeldingen":return this._renderAanmeldingenWidget();case"activiteiten":return this._renderActiviteitenWidget();default:return null}}_renderWidgets(){const e=this.config.show_widgets||["stats","schooltijden","volgende_schooldag","rooster_vandaag","huiswerk","cijfers","voortgangscijfers","opdrachten"],t=[];return e.includes("stats")&&t.push(this._renderStatsWidget()),e.includes("schooltijden")&&t.push(this._renderSchooltijdenWidget()),e.includes("week_schooltijden")&&t.push(this._renderWeekSchooltijdenWidget()),e.includes("volgende_schooldag")&&t.push(this._renderVolgendeSchooldagWidget()),e.includes("volgende_les")&&t.push(this._renderVolgendeLesWidget()),e.includes("rooster_vandaag")&&t.push(this._renderRoosterWidget()),e.includes("rooster_meta")&&t.push(this._renderRoosterMetaWidget()),e.includes("rooster_morgen")&&t.push(this._renderRoosterMorgenWidget()),e.includes("huiswerk")&&t.push(this._renderHuiswerkWidget()),e.includes("cijfers")&&t.push(this._renderCijfersWidget()),e.includes("voortgangscijfers")&&t.push(this._renderVoortgangscijfersWidget()),e.includes("opdrachten")&&t.push(this._renderOpdrachtenWidget()),e.includes("absenties")&&t.push(this._renderAbsentiesWidget()),e.includes("wijzigingen")&&t.push(this._renderWijzigingenWidget()),e.includes("aanmeldingen")&&t.push(this._renderAanmeldingenWidget()),e.includes("activiteiten")&&t.push(this._renderActiviteitenWidget()),t}_renderAfspraakItem(e){const t=!0===e.is_uitval,i=!t&&!0===e.was_afwijkend;return O`
      <div class="afspraak-item ${t?"uitval":""} ${i?"gewijzigd":""}">
        ${t?O`<div class="uitval-label">🚫 Vervallen</div>`:""}
        ${i?O`<div class="uitval-label">🔄 Gewijzigd</div>`:""}
        <div class="les-tijd">
          <strong>${this._formatTijd(e.start)} - ${this._formatTijd(e.einde)}</strong>
          ${e.is_online?O`<span class="badge badge-success">💻 Online</span>`:""}
          ${e.duurt_hele_dag?O`<span class="badge badge-warning">🕐 Hele dag</span>`:""}
        </div>
        <div class="les-omschrijving">${e.omschrijving}</div>
        ${e.opmerking?O`<div class="tijd">💬 ${e.opmerking}</div>`:""}
        ${e.lokaal?O`<div class="tijd">📍 ${e.lokaal}</div>`:""}
        ${e.is_huiswerk?O`<span class="badge">HW</span>`:""}
      </div>
    `}_renderRoosterWidget(){const e=this._data.afspraken||[],t=this._getVandaag(),i=e.filter(e=>this._getLocaleDateStr(e.start)===t);return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📅 Rooster Vandaag</h3>
          <span class="widget-icon">${i.length}</span>
        </div>
        <div class="widget-content">
          ${i.length>0?i.map(e=>this._renderAfspraakItem(e)):O`<div class="empty-state">Geen lessen vandaag 🎉</div>`}
        </div>
      </div>
    `}_nextSchoolDay(e){const t=(e||[]).filter(e=>"Les"===e.soort&&!e.is_uitval&&e.start&&"00:00:00"!==e.start.substr(11,8)),i=this._getVandaag(),s=[...new Set(t.map(e=>this._getLocaleDateStr(e.start)).filter(Boolean))].sort();return s.find(e=>e>=i)||null}_renderRoosterMetaWidget(){const e=this._data.afspraken||[],t=this._nextSchoolDay(e),i=t?e.filter(e=>this._getLocaleDateStr(e.start)===t):[],s=this._getVandaag(),a=this._getMorgen();let r;return r=t?t===s?"📅 Rooster (Vandaag)":t===a?"📅 Rooster (Morgen)":`📅 Rooster (${t})`:"📅 Rooster",O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">${r}</h3>
          <span class="widget-icon">${i.length}</span>
        </div>
        <div class="widget-content">
          ${i.length>0?i.map(e=>this._renderAfspraakItem(e)):O`<div class="empty-state">Geen lessen gevonden 🎉</div>`}
        </div>
      </div>
    `}_renderRoosterMorgenWidget(){const e=this._data.afspraken||[],t=this._getMorgen(),i=e.filter(e=>this._getLocaleDateStr(e.start)===t);return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📅 Rooster Morgen</h3>
          <span class="widget-icon">${i.length}</span>
        </div>
        <div class="widget-content">
          ${i.length>0?i.map(e=>this._renderAfspraakItem(e)):O`<div class="empty-state">Geen lessen morgen 🎉</div>`}
        </div>
      </div>
    `}_renderWeekSchooltijdenWidget(){const e=(this._data.afspraken||[]).filter(e=>"Les"===e.soort&&!e.is_uitval),t=["Maandag","Dinsdag","Woensdag","Donderdag","Vrijdag"].map((t,i)=>{const s=e.filter(e=>{const t=this._getLocaleDateStr(e.start);if(!t)return!1;const s=new Date(`${t}T12:00:00`).getDay();return(0===s?6:s-1)===i});if(0===s.length)return{name:t,start:null,end:null};const a=s.map(e=>e.start?.substr(11,5)).filter(Boolean).sort(),r=s.map(e=>e.einde?.substr(11,5)).filter(Boolean).sort();return{name:t,start:a[0],end:r[r.length-1]}});return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">Schooltijden per week</h3>
        </div>
        <div class="widget-content">
          ${t.map(e=>O`
            <div class="schoolweek-row">
              <span class="schoolweek-day">${e.name}</span>
              <span class="schoolweek-time">
                ${e.start&&e.end?`${e.start} - ${e.end}`:"Geen lessen"}
              </span>
            </div>
          `)}
        </div>
      </div>
    `}_renderVoortgangscijfersWidget(){const e=(this._data.voortgangscijfers||[]).slice().sort((e,t)=>(t.ingevoerd_op||"").localeCompare(e.ingevoerd_op||""));return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📈 Voortgangscijfers</h3>
          <span class="widget-icon">${e.length}</span>
        </div>
        <div class="widget-content">
          ${e.length>0?e.slice(0,10).map(e=>O`
              <div class="cijfer-item" style="${!1===e.is_voldoende?"border-left-color: var(--error-color);":""}">
                <div>
                  <span class="vak">${e.vak?.toUpperCase()}</span>: 
                  <span class="waarde">${e.waarde}</span>
                  ${e.weegfactor?O` <span class="wf">(x${e.weegfactor})</span>`:""}
                  ${e.vrijstelling?O`<span class="badge badge-warning">Vrijstelling</span>`:""}
                </div>
                <div class="tijd">
                  ${e.omschrijving}${e.periode?` · ${e.periode}`:""}
                  ${e.ingevoerd_op?` - ${e.ingevoerd_op.substr(0,10)}`:""}
                </div>
              </div>
            `):O`<div class="empty-state">Nog geen cijfers dit schooljaar</div>`}
        </div>
      </div>
    `}_renderHuiswerkWidget(){const e=(this._data.afspraken||[]).filter(e=>!0===e.is_huiswerk),t=e.filter(e=>!0!==e.is_afgerond),i=e.length-t.length;return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📚 Huiswerk</h3>
          <span class="widget-icon">${t.length}</span>
        </div>
        <div class="widget-content">
          ${t.length>0?t.slice(0,8).map(e=>O`
              <div class="afspraak-item">
                <div>
                  <strong>${e.omschrijving}</strong>
                  ${e.is_online?O`<span class="badge badge-success">💻 Online</span>`:""}
                </div>
                ${e.inhoud?O`<div class="tijd">${e.inhoud}</div>`:""}
                <div class="tijd">📅 ${e.start?.substr(0,10)} · ${this._formatTijd(e.start)}</div>
              </div>
            `):O`<div class="empty-state">Geen open huiswerk 🎉</div>`}
          ${i>0?O`<div class="tijd" style="margin-top: 8px;">✅ ${i} afgerond</div>`:""}
        </div>
      </div>
    `}_renderCijfersWidget(){const e=this._data.cijfers||[];return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">🎓 Recente Cijfers</h3>
          <span class="widget-icon">${e.length}</span>
        </div>
        <div class="widget-content">
          ${e.length>0?e.slice(0,5).map(e=>O`
              <div class="cijfer-item">
                <div>
                  <span class="vak">${e.vak?.toUpperCase()}</span>: 
                  <span class="waarde">${e.waarde}</span>
                  ${e.weegfactor?O` <span class="wf">(x${e.weegfactor})</span>`:""}
                </div>
                <div class="tijd">${e.omschrijving} - ${e.ingevoerd_op?.substr(0,10)}</div>
              </div>
            `):O`<div class="empty-state">Geen cijfers beschikbaar</div>`}
        </div>
      </div>
    `}_renderOpdrachtenWidget(){const e=(this._data.opdrachten||[]).filter(e=>!e.ingeleverd_op);return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📝 Open Opdrachten</h3>
          <span class="widget-icon">${e.length}</span>
        </div>
        <div class="widget-content">
          ${e.length>0?e.slice(0,5).map(e=>{const t=(new Date(e.inleveren_voor)-new Date)/864e5,i=t<1,s=t<2;return O`
                <div class="opdracht-item" style="${i?"border-left-color: var(--error-color); background: rgba(244, 67, 54, 0.1);":s?"border-left-color: var(--warning-color); background: rgba(255, 152, 0, 0.1);":""}">
                  <div>
                    <strong>${e.titel}</strong> 
                    ${i?O`<span class="badge">SPOED!</span>`:s?O`<span class="badge badge-warning">BIJNA!</span>`:""}
                  </div>
                  <div class="tijd">Vak: ${e.vak?.toUpperCase()}</div>
                  <div class="tijd">📅 ${e.inleveren_voor?.substr(0,16)}</div>
                </div>
              `}):O`<div class="empty-state">Geen open opdrachten ✅</div>`}
        </div>
      </div>
    `}_renderAbsentiesWidget(){const e=(this._data.absenties||[]).slice().sort((e,t)=>(t.start||"").localeCompare(e.start||""));return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">⚠️ Recente Absenties</h3>
          <span class="widget-icon">${e.length}</span>
        </div>
        <div class="widget-content">
          ${e.length>0?e.slice(0,5).map(e=>O`
              <div class="afspraak-item" style="${!1===e.geoorloofd?"border-left-color: var(--error-color); background: rgba(244, 67, 54, 0.06);":""}">
                <div>
                  <strong>${e.start?.substr(0,10)}</strong>
                  ${e.lesuur?O`<span class="tijd"> · ${e.lesuur}e uur</span>`:""}
                </div>
                <div>${e.omschrijving}</div>
                <div>
                  ${e.code?O`<span class="badge">${e.code.toUpperCase()}</span>`:""}
                  ${!1===e.geoorloofd?O`<span class="badge">Ongeoorloofd</span>`:O`<span class="badge badge-success">Geoorloofd</span>`}
                </div>
                ${e.afspraak?O`<div class="tijd">${e.afspraak}</div>`:""}
              </div>
            `):O`<div class="empty-state">Geen recente absenties 👍</div>`}
        </div>
      </div>
    `}_renderWijzigingenWidget(){const e=this._data.wijzigingen||[];return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">🔄 Roosterwijzigingen</h3>
          <span class="widget-icon">${e.length}</span>
        </div>
        <div class="widget-content">
          ${e.length>0?e.slice(-3).map(e=>this._renderAfspraakItem(e)):O`<div class="empty-state">Geen wijzigingen</div>`}
        </div>
      </div>
    `}_renderStatsWidget(){return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📊 Overzicht</h3>
          <span class="widget-icon">📈</span>
        </div>
        <div class="widget-content">
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📅 Lessen vandaag:</span>
              <strong style="color: var(--accent-color);">${this._data.aantal_afspraken_vandaag||0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📚 Huiswerk open:</span>
              <strong style="color: var(--accent-color);">${this._data.aantal_huiswerk_onafgerond??this._data.aantal_huiswerk??0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>✅ Huiswerk afgerond:</span>
              <strong style="color: var(--accent-color);">${this._data.aantal_huiswerk_afgerond||0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>🎓 Cijfers:</span>
              <strong style="color: var(--accent-color);">${this._data.cijfers?.length||0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📈 Cijfers dit jaar:</span>
              <strong style="color: var(--accent-color);">${this._data.voortgangscijfers?.length||0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📝 Opdrachten:</span>
              <strong style="color: var(--accent-color);">${this._data.opdrachten?.length||0}</strong>
            </div>
          </div>
        </div>
      </div>
    `}_renderVolgendeLesWidget(){return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">⏰ Volgende Les</h3>
          <span class="widget-icon">🕒</span>
        </div>
        <div class="widget-content">
          ${this._data.volgende_afspraak&&"Geen"!==this._data.volgende_afspraak?O`
              <div style="text-align: center; padding: 20px;">
                <div style="font-size: 1.4em; font-weight: bold; color: var(--accent-color); margin-bottom: 8px;">
                  ${this._data.volgende_afspraak}
                </div>
                ${this._data.volgende_vak?O`
                  <div style="font-size: 1.1em; color: var(--primary-text-color); margin-bottom: 16px;">
                    ${this._data.volgende_vak}
                  </div>
                `:""}
                <div style="background: var(--primary-color); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block;">
                  🎯 Komende les
                </div>
              </div>
            `:O`<div class="empty-state">Geen komende lessen 🎉</div>`}
        </div>
      </div>
    `}_renderAanmeldingenWidget(){const e=this._data.aanmeldingen||[];return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">🏫 Aanmeldingen</h3>
          <span class="widget-icon">${e.length}</span>
        </div>
        <div class="widget-content">
          ${e.length>0?e.slice(0,3).map(e=>O`
              <div class="afspraak-item">
                <div><strong>${e.start} - ${e.einde}</strong></div>
                <div>${e.studie||""}</div>
                <div class="tijd">${e.lesperiode||""}</div>
              </div>
            `):O`<div class="empty-state">Geen aanmeldingen</div>`}
        </div>
      </div>
    `}_renderActiviteitenWidget(){const e=this._data.activiteiten||[];return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📢 Activiteiten</h3>
          <span class="widget-icon">${e.length}</span>
        </div>
        <div class="widget-content">
          ${e.length>0?e.slice(0,3).map(e=>O`
              <div class="afspraak-item">
                <div><strong>${e.titel}</strong></div>
                <div class="tijd">Zichtbaar: ${e.zichtbaar_vanaf} t/m ${e.zichtbaar_tot}</div>
              </div>
            `):O`<div class="empty-state">Geen activiteiten</div>`}
        </div>
      </div>
    `}_renderSchooltijdenWidget(){const e=this._data.school_start_vandaag||"Geen",t=this._data.school_einde_vandaag||"Geen",i=this._data.lessen_vandaag||[];return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">🏫 Schooltijden Vandaag</h3>
          <span class="widget-icon">${i.length}</span>
        </div>
        <div class="widget-content">
          <div class="afspraak-item" style="border-left: 4px solid var(--success-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>⏰ Eerste les:</span>
              <strong style="color: var(--accent-color);">${e}</strong>
            </div>
          </div>
          <div class="afspraak-item" style="border-left: 4px solid var(--warning-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>🔔 Laatste les:</span>
              <strong style="color: var(--accent-color);">${t}</strong>
            </div>
          </div>
          ${i.length>0?i.map(e=>O`
            <div class="afspraak-item" style="border-left: 4px solid var(--primary-color);">
              <div><strong>${e.start} - ${e.einde}</strong> ${e.vak?O`<span class="vak">${e.vak}</span>`:""}</div>
              ${e.omschrijving?O`<div>${e.omschrijving}</div>`:""}
              ${e.lokaal?O`<div class="tijd">📍 ${e.lokaal}</div>`:""}
            </div>
          `):O`<div class="empty-state">Geen lessen vandaag 🎉</div>`}
        </div>
      </div>
    `}_renderVolgendeSchooldagWidget(){const e=this._data.volgende_schooldag||"Geen",t=this._data.volgende_schooldag_start||"Geen",i=this._data.volgende_schooldag_einde||"Geen";return O`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📆 Volgende Schooldag</h3>
          <span class="widget-icon">→</span>
        </div>
        <div class="widget-content">
          <div class="afspraak-item" style="border-left: 4px solid var(--accent-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📅 Datum:</span>
              <strong style="color: var(--accent-color);">${e}</strong>
            </div>
          </div>
          <div class="afspraak-item" style="border-left: 4px solid var(--success-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>⏰ Eerste les:</span>
              <strong style="color: var(--accent-color);">${t}</strong>
            </div>
          </div>
          <div class="afspraak-item" style="border-left: 4px solid var(--warning-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>🔔 Laatste les:</span>
              <strong style="color: var(--accent-color);">${i}</strong>
            </div>
          </div>
          ${"Geen"===e?O`<div class="empty-state">Geen komende schooldag gevonden</div>`:""}
        </div>
      </div>
    `}}customElements.define("magister-school-card",re);
//# sourceMappingURL=magister-school-card.js.map

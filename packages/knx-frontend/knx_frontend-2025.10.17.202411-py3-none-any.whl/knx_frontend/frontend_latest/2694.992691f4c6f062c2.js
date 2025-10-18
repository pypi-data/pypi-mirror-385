export const __webpack_id__="2694";export const __webpack_ids__=["2694"];export const __webpack_modules__={26846:function(t,o,e){function a(t){return null==t||Array.isArray(t)?t:[t]}e.d(o,{e:()=>a})},10763:function(t,o,e){e.d(o,{x:()=>a});const a=(t,o)=>t&&t.config.components.includes(o)},81411:function(t,o,e){e.d(o,{a:()=>i});const a=(0,e(42109).n)((t=>{history.replaceState({scrollPosition:t},"")}),300);function i(t){return(o,e)=>{if("object"==typeof e)throw new Error("This decorator does not support this compilation type.");const i=o.connectedCallback;o.connectedCallback=function(){i.call(this);const o=this[e];o&&this.updateComplete.then((()=>{const e=this.renderRoot.querySelector(t);e&&setTimeout((()=>{e.scrollTop=o}),0)}))};const r=Object.getOwnPropertyDescriptor(o,e);let n;if(void 0===r)n={get(){return this[`__${String(e)}`]||history.state?.scrollPosition},set(t){a(t),this[`__${String(e)}`]=t},configurable:!0,enumerable:!0};else{const t=r.set;n={...r,set(o){a(o),this[`__${String(e)}`]=o,t?.call(this,o)}}}Object.defineProperty(o,e,n)}}},42109:function(t,o,e){e.d(o,{n:()=>a});const a=(t,o,e=!0,a=!0)=>{let i,r=0;const n=(...n)=>{const s=()=>{r=!1===e?0:Date.now(),i=void 0,t(...n)},l=Date.now();r||!1!==e||(r=l);const c=o-(l-r);c<=0||c>o?(i&&(clearTimeout(i),i=void 0),r=l,t(...n)):i||!1===a||(i=window.setTimeout(s,c))};return n.cancel=()=>{clearTimeout(i),i=void 0,r=0},n}},8101:function(t,o,e){e.r(o),e.d(o,{HaIconButtonArrowPrev:()=>s});var a=e(69868),i=e(84922),r=e(11991),n=e(90933);e(93672);class s extends i.WF{render(){return i.qy`
      <ha-icon-button
        .disabled=${this.disabled}
        .label=${this.label||this.hass?.localize("ui.common.back")||"Back"}
        .path=${this._icon}
      ></ha-icon-button>
    `}constructor(...t){super(...t),this.disabled=!1,this._icon="rtl"===n.G.document.dir?"M4,11V13H16L10.5,18.5L11.92,19.92L19.84,12L11.92,4.08L10.5,5.5L16,11H4Z":"M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"}}(0,a.__decorate)([(0,r.MZ)({attribute:!1})],s.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],s.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.MZ)()],s.prototype,"label",void 0),(0,a.__decorate)([(0,r.wk)()],s.prototype,"_icon",void 0),s=(0,a.__decorate)([(0,r.EM)("ha-icon-button-arrow-prev")],s)},93672:function(t,o,e){e.r(o),e.d(o,{HaIconButton:()=>s});var a=e(69868),i=(e(31807),e(84922)),r=e(11991),n=e(13802);e(95635);class s extends i.WF{focus(){this._button?.focus()}render(){return i.qy`
      <mwc-icon-button
        aria-label=${(0,n.J)(this.label)}
        title=${(0,n.J)(this.hideTitle?void 0:this.label)}
        aria-haspopup=${(0,n.J)(this.ariaHasPopup)}
        .disabled=${this.disabled}
      >
        ${this.path?i.qy`<ha-svg-icon .path=${this.path}></ha-svg-icon>`:i.qy`<slot></slot>`}
      </mwc-icon-button>
    `}constructor(...t){super(...t),this.disabled=!1,this.hideTitle=!1}}s.shadowRootOptions={mode:"open",delegatesFocus:!0},s.styles=i.AH`
    :host {
      display: inline-block;
      outline: none;
    }
    :host([disabled]) {
      pointer-events: none;
    }
    mwc-icon-button {
      --mdc-theme-on-primary: currentColor;
      --mdc-theme-text-disabled-on-light: var(--disabled-text-color);
    }
  `,(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],s.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.MZ)({type:String})],s.prototype,"path",void 0),(0,a.__decorate)([(0,r.MZ)({type:String})],s.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)({type:String,attribute:"aria-haspopup"})],s.prototype,"ariaHasPopup",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:"hide-title",type:Boolean})],s.prototype,"hideTitle",void 0),(0,a.__decorate)([(0,r.P)("mwc-icon-button",!0)],s.prototype,"_button",void 0),s=(0,a.__decorate)([(0,r.EM)("ha-icon-button")],s)},3433:function(t,o,e){var a=e(69868),i=e(84922),r=e(11991),n=e(73120);class s{processMessage(t){if("removed"===t.type)for(const o of Object.keys(t.notifications))delete this.notifications[o];else this.notifications={...this.notifications,...t.notifications};return Object.values(this.notifications)}constructor(){this.notifications={}}}e(93672);class l extends i.WF{connectedCallback(){super.connectedCallback(),this._attachNotifOnConnect&&(this._attachNotifOnConnect=!1,this._subscribeNotifications())}disconnectedCallback(){super.disconnectedCallback(),this._unsubNotifications&&(this._attachNotifOnConnect=!0,this._unsubNotifications(),this._unsubNotifications=void 0)}render(){if(!this._show)return i.s6;const t=this._hasNotifications&&(this.narrow||"always_hidden"===this.hass.dockedSidebar);return i.qy`
      <ha-icon-button
        .label=${this.hass.localize("ui.sidebar.sidebar_toggle")}
        .path=${"M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"}
        @click=${this._toggleMenu}
      ></ha-icon-button>
      ${t?i.qy`<div class="dot"></div>`:""}
    `}firstUpdated(t){super.firstUpdated(t),this.hassio&&(this._alwaysVisible=(Number(window.parent.frontendVersion)||0)<20190710)}willUpdate(t){if(super.willUpdate(t),!t.has("narrow")&&!t.has("hass"))return;const o=t.has("hass")?t.get("hass"):this.hass,e=(t.has("narrow")?t.get("narrow"):this.narrow)||"always_hidden"===o?.dockedSidebar,a=this.narrow||"always_hidden"===this.hass.dockedSidebar;this.hasUpdated&&e===a||(this._show=a||this._alwaysVisible,a?this._subscribeNotifications():this._unsubNotifications&&(this._unsubNotifications(),this._unsubNotifications=void 0))}_subscribeNotifications(){if(this._unsubNotifications)throw new Error("Already subscribed");this._unsubNotifications=((t,o)=>{const e=new s,a=t.subscribeMessage((t=>o(e.processMessage(t))),{type:"persistent_notification/subscribe"});return()=>{a.then((t=>t?.()))}})(this.hass.connection,(t=>{this._hasNotifications=t.length>0}))}_toggleMenu(){(0,n.r)(this,"hass-toggle-menu")}constructor(...t){super(...t),this.hassio=!1,this.narrow=!1,this._hasNotifications=!1,this._show=!1,this._alwaysVisible=!1,this._attachNotifOnConnect=!1}}l.styles=i.AH`
    :host {
      position: relative;
    }
    .dot {
      pointer-events: none;
      position: absolute;
      background-color: var(--accent-color);
      width: 12px;
      height: 12px;
      top: 9px;
      right: 7px;
      inset-inline-end: 7px;
      inset-inline-start: initial;
      border-radius: 50%;
      border: 2px solid var(--app-header-background-color);
    }
  `,(0,a.__decorate)([(0,r.MZ)({type:Boolean})],l.prototype,"hassio",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],l.prototype,"narrow",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,a.__decorate)([(0,r.wk)()],l.prototype,"_hasNotifications",void 0),(0,a.__decorate)([(0,r.wk)()],l.prototype,"_show",void 0),l=(0,a.__decorate)([(0,r.EM)("ha-menu-button")],l)},95635:function(t,o,e){e.r(o),e.d(o,{HaSvgIcon:()=>n});var a=e(69868),i=e(84922),r=e(11991);class n extends i.WF{render(){return i.JW`
    <svg
      viewBox=${this.viewBox||"0 0 24 24"}
      preserveAspectRatio="xMidYMid meet"
      focusable="false"
      role="img"
      aria-hidden="true"
    >
      <g>
        ${this.path?i.JW`<path class="primary-path" d=${this.path}></path>`:i.s6}
        ${this.secondaryPath?i.JW`<path class="secondary-path" d=${this.secondaryPath}></path>`:i.s6}
      </g>
    </svg>`}}n.styles=i.AH`
    :host {
      display: var(--ha-icon-display, inline-flex);
      align-items: center;
      justify-content: center;
      position: relative;
      vertical-align: middle;
      fill: var(--icon-primary-color, currentcolor);
      width: var(--mdc-icon-size, 24px);
      height: var(--mdc-icon-size, 24px);
    }
    svg {
      width: 100%;
      height: 100%;
      pointer-events: none;
      display: block;
    }
    path.primary-path {
      opacity: var(--icon-primary-opactity, 1);
    }
    path.secondary-path {
      fill: var(--icon-secondary-color, currentcolor);
      opacity: var(--icon-secondary-opactity, 0.5);
    }
  `,(0,a.__decorate)([(0,r.MZ)()],n.prototype,"path",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"secondaryPath",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"viewBox",void 0),n=(0,a.__decorate)([(0,r.EM)("ha-svg-icon")],n)},54885:function(t,o,e){var a=e(69868),i=e(84922),r=e(11991),n=e(75907),s=e(65940),l=e(26846),c=e(10763);const h=(t,o)=>!o.component||(0,l.e)(o.component).some((o=>(0,c.x)(t,o))),d=(t,o)=>!o.not_component||!(0,l.e)(o.not_component).some((o=>(0,c.x)(t,o))),p=t=>t.core,b=(t,o)=>(t=>t.advancedOnly)(o)&&!(t=>t.userData?.showAdvanced)(t);var v=e(68985),u=e(81411),f=(e(8101),e(3433),e(95635),e(13802)),m=e(41616),g=e(42208),y=e(67051);class _ extends g.n{attach(t){super.attach(t),this.attachableTouchController.attach(t)}disconnectedCallback(){super.disconnectedCallback(),this.hovered=!1,this.pressed=!1}detach(){super.detach(),this.attachableTouchController.detach()}_onTouchControlChange(t,o){t?.removeEventListener("touchend",this._handleTouchEnd),o?.addEventListener("touchend",this._handleTouchEnd)}constructor(...t){super(...t),this.attachableTouchController=new m.i(this,this._onTouchControlChange.bind(this)),this._handleTouchEnd=()=>{this.disabled||super.endPressAnimation()}}}_.styles=[y.R,i.AH`
      :host {
        --md-ripple-hover-opacity: var(--ha-ripple-hover-opacity, 0.08);
        --md-ripple-pressed-opacity: var(--ha-ripple-pressed-opacity, 0.12);
        --md-ripple-hover-color: var(
          --ha-ripple-hover-color,
          var(--ha-ripple-color, var(--secondary-text-color))
        );
        --md-ripple-pressed-color: var(
          --ha-ripple-pressed-color,
          var(--ha-ripple-color, var(--secondary-text-color))
        );
      }
    `],_=(0,a.__decorate)([(0,r.EM)("ha-ripple")],_);class w extends i.WF{render(){return i.qy`
      <div
        tabindex="0"
        role="tab"
        aria-selected=${this.active}
        aria-label=${(0,f.J)(this.name)}
        @keydown=${this._handleKeyDown}
      >
        ${this.narrow?i.qy`<slot name="icon"></slot>`:""}
        <span class="name">${this.name}</span>
        <ha-ripple></ha-ripple>
      </div>
    `}_handleKeyDown(t){"Enter"===t.key&&t.target.click()}constructor(...t){super(...t),this.active=!1,this.narrow=!1}}w.styles=i.AH`
    div {
      padding: 0 32px;
      display: flex;
      flex-direction: column;
      text-align: center;
      box-sizing: border-box;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--header-height);
      cursor: pointer;
      position: relative;
      outline: none;
    }

    .name {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }

    :host([active]) {
      color: var(--primary-color);
    }

    :host(:not([narrow])[active]) div {
      border-bottom: 2px solid var(--primary-color);
    }

    :host([narrow]) {
      min-width: 0;
      display: flex;
      justify-content: center;
      overflow: hidden;
    }

    :host([narrow]) div {
      padding: 0 4px;
    }

    div:focus-visible:before {
      position: absolute;
      display: block;
      content: "";
      inset: 0;
      background-color: var(--secondary-text-color);
      opacity: 0.08;
    }
  `,(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],w.prototype,"active",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],w.prototype,"narrow",void 0),(0,a.__decorate)([(0,r.MZ)()],w.prototype,"name",void 0),w=(0,a.__decorate)([(0,r.EM)("ha-tab")],w);var x=e(83566);class k extends i.WF{willUpdate(t){t.has("route")&&(this._activeTab=this.tabs.find((t=>`${this.route.prefix}${this.route.path}`.includes(t.path)))),super.willUpdate(t)}render(){const t=this._getTabs(this.tabs,this._activeTab,this.hass.config.components,this.hass.language,this.hass.userData,this.narrow,this.localizeFunc||this.hass.localize),o=t.length>1;return i.qy`
      <div class="toolbar">
        <slot name="toolbar">
          <div class="toolbar-content">
            ${this.mainPage||!this.backPath&&history.state?.root?i.qy`
                  <ha-menu-button
                    .hassio=${this.supervisor}
                    .hass=${this.hass}
                    .narrow=${this.narrow}
                  ></ha-menu-button>
                `:this.backPath?i.qy`
                    <a href=${this.backPath}>
                      <ha-icon-button-arrow-prev
                        .hass=${this.hass}
                      ></ha-icon-button-arrow-prev>
                    </a>
                  `:i.qy`
                    <ha-icon-button-arrow-prev
                      .hass=${this.hass}
                      @click=${this._backTapped}
                    ></ha-icon-button-arrow-prev>
                  `}
            ${this.narrow||!o?i.qy`<div class="main-title">
                  <slot name="header">${o?"":t[0]}</slot>
                </div>`:""}
            ${o&&!this.narrow?i.qy`<div id="tabbar">${t}</div>`:""}
            <div id="toolbar-icon">
              <slot name="toolbar-icon"></slot>
            </div>
          </div>
        </slot>
        ${o&&this.narrow?i.qy`<div id="tabbar" class="bottom-bar">${t}</div>`:""}
      </div>
      <div
        class=${(0,n.H)({container:!0,tabs:o&&this.narrow})}
      >
        ${this.pane?i.qy`<div class="pane">
              <div class="shadow-container"></div>
              <div class="ha-scrollbar">
                <slot name="pane"></slot>
              </div>
            </div>`:i.s6}
        <div
          class="content ha-scrollbar ${(0,n.H)({tabs:o})}"
          @scroll=${this._saveScrollPos}
        >
          <slot></slot>
          ${this.hasFab?i.qy`<div class="fab-bottom-space"></div>`:i.s6}
        </div>
      </div>
      <div id="fab" class=${(0,n.H)({tabs:o})}>
        <slot name="fab"></slot>
      </div>
    `}_saveScrollPos(t){this._savedScrollPos=t.target.scrollTop}_backTapped(){this.backCallback?this.backCallback():(0,v.O)()}static get styles(){return[x.dp,i.AH`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
        }

        :host([narrow]) {
          width: 100%;
          position: fixed;
        }

        .container {
          display: flex;
          height: calc(
            100% - var(--header-height, 0px) - var(--safe-area-inset-top, 0px)
          );
        }

        ha-menu-button {
          margin-right: 24px;
          margin-inline-end: 24px;
          margin-inline-start: initial;
        }

        .toolbar {
          font-size: var(--ha-font-size-xl);
          height: calc(
            var(--header-height, 0px) + var(--safe-area-inset-top, 0px)
          );
          padding-top: var(--safe-area-inset-top);
          padding-right: var(--safe-area-inset-right);
          background-color: var(--sidebar-background-color);
          font-weight: var(--ha-font-weight-normal);
          border-bottom: 1px solid var(--divider-color);
          box-sizing: border-box;
        }
        :host([narrow]) .toolbar {
          padding-left: var(--safe-area-inset-left);
        }
        .toolbar-content {
          padding: 8px 12px;
          display: flex;
          align-items: center;
          height: 100%;
          box-sizing: border-box;
        }
        :host([narrow]) .toolbar-content {
          padding: 4px;
        }
        .toolbar a {
          color: var(--sidebar-text-color);
          text-decoration: none;
        }
        .bottom-bar a {
          width: 25%;
        }

        #tabbar {
          display: flex;
          font-size: var(--ha-font-size-m);
          overflow: hidden;
        }

        #tabbar > a {
          overflow: hidden;
          max-width: 45%;
        }

        #tabbar.bottom-bar {
          position: absolute;
          bottom: 0;
          left: 0;
          padding: 0 16px;
          box-sizing: border-box;
          background-color: var(--sidebar-background-color);
          border-top: 1px solid var(--divider-color);
          justify-content: space-around;
          z-index: 2;
          font-size: var(--ha-font-size-s);
          width: 100%;
          padding-bottom: var(--safe-area-inset-bottom);
        }

        #tabbar:not(.bottom-bar) {
          flex: 1;
          justify-content: center;
        }

        :host(:not([narrow])) #toolbar-icon {
          min-width: 40px;
        }

        ha-menu-button,
        ha-icon-button-arrow-prev,
        ::slotted([slot="toolbar-icon"]) {
          display: flex;
          flex-shrink: 0;
          pointer-events: auto;
          color: var(--sidebar-icon-color);
        }

        .main-title {
          flex: 1;
          max-height: var(--header-height);
          line-height: var(--ha-line-height-normal);
          color: var(--sidebar-text-color);
          margin: var(--main-title-margin, var(--margin-title));
        }

        .content {
          position: relative;
          width: 100%;
          margin-right: var(--safe-area-inset-right);
          margin-inline-end: var(--safe-area-inset-right);
          margin-bottom: var(--safe-area-inset-bottom);
          overflow: auto;
          -webkit-overflow-scrolling: touch;
        }
        :host([narrow]) .content {
          margin-left: var(--safe-area-inset-left);
          margin-inline-start: var(--safe-area-inset-left);
        }
        :host([narrow]) .content.tabs {
          /* Bottom bar reuses header height */
          margin-bottom: calc(
            var(--header-height, 0px) + var(--safe-area-inset-bottom, 0px)
          );
        }

        .content .fab-bottom-space {
          height: calc(64px + var(--safe-area-inset-bottom, 0px));
        }

        :host([narrow]) .content.tabs .fab-bottom-space {
          height: calc(80px + var(--safe-area-inset-bottom, 0px));
        }

        #fab {
          position: fixed;
          right: calc(16px + var(--safe-area-inset-right, 0px));
          inset-inline-end: calc(16px + var(--safe-area-inset-right));
          inset-inline-start: initial;
          bottom: calc(16px + var(--safe-area-inset-bottom, 0px));
          z-index: 1;
          display: flex;
          flex-wrap: wrap;
          justify-content: flex-end;
          gap: 8px;
        }
        :host([narrow]) #fab.tabs {
          bottom: calc(84px + var(--safe-area-inset-bottom, 0px));
        }
        #fab[is-wide] {
          bottom: 24px;
          right: 24px;
          inset-inline-end: 24px;
          inset-inline-start: initial;
        }

        .pane {
          border-right: 1px solid var(--divider-color);
          border-inline-end: 1px solid var(--divider-color);
          border-inline-start: initial;
          box-sizing: border-box;
          display: flex;
          flex: 0 0 var(--sidepane-width, 250px);
          width: var(--sidepane-width, 250px);
          flex-direction: column;
          position: relative;
        }
        .pane .ha-scrollbar {
          flex: 1;
        }
      `]}constructor(...t){super(...t),this.supervisor=!1,this.mainPage=!1,this.narrow=!1,this.isWide=!1,this.pane=!1,this.hasFab=!1,this._getTabs=(0,s.A)(((t,o,e,a,r,n,s)=>{const l=t.filter((t=>((t,o)=>(p(o)||h(t,o))&&!b(t,o)&&d(t,o))(this.hass,t)));if(l.length<2){if(1===l.length){const t=l[0];return[t.translationKey?s(t.translationKey):t.name]}return[""]}return l.map((t=>i.qy`
          <a href=${t.path}>
            <ha-tab
              .hass=${this.hass}
              .active=${t.path===o?.path}
              .narrow=${this.narrow}
              .name=${t.translationKey?s(t.translationKey):t.name}
            >
              ${t.iconPath?i.qy`<ha-svg-icon
                    slot="icon"
                    .path=${t.iconPath}
                  ></ha-svg-icon>`:""}
            </ha-tab>
          </a>
        `))}))}}(0,a.__decorate)([(0,r.MZ)({attribute:!1})],k.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],k.prototype,"supervisor",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],k.prototype,"localizeFunc",void 0),(0,a.__decorate)([(0,r.MZ)({type:String,attribute:"back-path"})],k.prototype,"backPath",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],k.prototype,"backCallback",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,attribute:"main-page"})],k.prototype,"mainPage",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],k.prototype,"route",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],k.prototype,"tabs",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],k.prototype,"narrow",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"is-wide"})],k.prototype,"isWide",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],k.prototype,"pane",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,attribute:"has-fab"})],k.prototype,"hasFab",void 0),(0,a.__decorate)([(0,r.wk)()],k.prototype,"_activeTab",void 0),(0,a.__decorate)([(0,u.a)(".content")],k.prototype,"_savedScrollPos",void 0),(0,a.__decorate)([(0,r.Ls)({passive:!0})],k.prototype,"_saveScrollPos",null),k=(0,a.__decorate)([(0,r.EM)("hass-tabs-subpage")],k)},83566:function(t,o,e){e.d(o,{RF:()=>r,dp:()=>s,nA:()=>n,og:()=>i});var a=e(84922);const i=a.AH`
  button.link {
    background: none;
    color: inherit;
    border: none;
    padding: 0;
    font: inherit;
    text-align: left;
    text-decoration: underline;
    cursor: pointer;
    outline: none;
  }
`,r=a.AH`
  :host {
    font-family: var(--ha-font-family-body);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    font-size: var(--ha-font-size-m);
    font-weight: var(--ha-font-weight-normal);
    line-height: var(--ha-line-height-normal);
  }

  app-header div[sticky] {
    height: 48px;
  }

  app-toolbar [main-title] {
    margin-left: 20px;
    margin-inline-start: 20px;
    margin-inline-end: initial;
  }

  h1 {
    font-family: var(--ha-font-family-heading);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    font-size: var(--ha-font-size-2xl);
    font-weight: var(--ha-font-weight-normal);
    line-height: var(--ha-line-height-condensed);
  }

  h2 {
    font-family: var(--ha-font-family-body);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: var(--ha-font-size-xl);
    font-weight: var(--ha-font-weight-medium);
    line-height: var(--ha-line-height-normal);
  }

  h3 {
    font-family: var(--ha-font-family-body);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    font-size: var(--ha-font-size-l);
    font-weight: var(--ha-font-weight-normal);
    line-height: var(--ha-line-height-normal);
  }

  a {
    color: var(--primary-color);
  }

  .secondary {
    color: var(--secondary-text-color);
  }

  .error {
    color: var(--error-color);
  }

  .warning {
    color: var(--error-color);
  }

  ${i}

  .card-actions a {
    text-decoration: none;
  }

  .card-actions .warning {
    --mdc-theme-primary: var(--error-color);
  }

  .layout.horizontal,
  .layout.vertical {
    display: flex;
  }
  .layout.inline {
    display: inline-flex;
  }
  .layout.horizontal {
    flex-direction: row;
  }
  .layout.vertical {
    flex-direction: column;
  }
  .layout.wrap {
    flex-wrap: wrap;
  }
  .layout.no-wrap {
    flex-wrap: nowrap;
  }
  .layout.center,
  .layout.center-center {
    align-items: center;
  }
  .layout.bottom {
    align-items: flex-end;
  }
  .layout.center-justified,
  .layout.center-center {
    justify-content: center;
  }
  .flex {
    flex: 1;
    flex-basis: 0.000000001px;
  }
  .flex-auto {
    flex: 1 1 auto;
  }
  .flex-none {
    flex: none;
  }
  .layout.justified {
    justify-content: space-between;
  }
`,n=a.AH`
  /* mwc-dialog (ha-dialog) styles */
  ha-dialog {
    --mdc-dialog-min-width: 400px;
    --mdc-dialog-max-width: 600px;
    --mdc-dialog-max-width: min(600px, 95vw);
    --justify-action-buttons: space-between;
  }

  ha-dialog .form {
    color: var(--primary-text-color);
  }

  a {
    color: var(--primary-color);
  }

  /* make dialog fullscreen on small screens */
  @media all and (max-width: 450px), all and (max-height: 500px) {
    ha-dialog {
      --mdc-dialog-min-width: 100vw;
      --mdc-dialog-max-width: 100vw;
      --mdc-dialog-min-height: 100%;
      --mdc-dialog-max-height: 100%;
      --vertical-align-dialog: flex-end;
      --ha-dialog-border-radius: 0;
    }
  }
  .error {
    color: var(--error-color);
  }
`,s=a.AH`
  .ha-scrollbar::-webkit-scrollbar {
    width: 0.4rem;
    height: 0.4rem;
  }

  .ha-scrollbar::-webkit-scrollbar-thumb {
    -webkit-border-radius: 4px;
    border-radius: 4px;
    background: var(--scrollbar-thumb-color);
  }

  .ha-scrollbar {
    overflow-y: auto;
    scrollbar-color: var(--scrollbar-thumb-color) transparent;
    scrollbar-width: thin;
  }
`;a.AH`
  body {
    background-color: var(--primary-background-color);
    color: var(--primary-text-color);
    height: calc(100vh - 32px);
    width: 100vw;
  }
`}};
//# sourceMappingURL=2694.992691f4c6f062c2.js.map
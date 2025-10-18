"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1092"],{3371:function(e,t,i){i.d(t,{d:function(){return a}});const a=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},81571:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(65315),i(37089),i(95013);var a=i(69868),o=i(76440),r=i(84922),s=i(11991),l=i(75907),n=i(73120),d=i(76943),c=(i(93672),i(3371)),p=i(26846),h=i(88234),u=e([o,d]);[o,d]=u.then?(await u)():u;let g,v,m,_,f,y,b,$,x=e=>e;const M="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",k="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z";class w extends r.WF{firstUpdated(e){super.firstUpdated(e),this.autoOpenFileDialog&&this._openFilePicker()}get _name(){if(void 0===this.value)return"";if("string"==typeof this.value)return this.value;return(this.value instanceof FileList?Array.from(this.value):(0,p.e)(this.value)).map((e=>e.name)).join(", ")}render(){const e=this.localize||this.hass.localize;return(0,r.qy)(g||(g=x`
      ${0}
    `),this.uploading?(0,r.qy)(v||(v=x`<div class="container">
            <div class="uploading">
              <span class="header"
                >${0}</span
              >
              ${0}
            </div>
            <mwc-linear-progress
              .indeterminate=${0}
              .progress=${0}
            ></mwc-linear-progress>
          </div>`),this.uploadingLabel||(this.value?e("ui.components.file-upload.uploading_name",{name:this._name}):e("ui.components.file-upload.uploading")),this.progress?(0,r.qy)(m||(m=x`<div class="progress">
                    ${0}${0}%
                  </div>`),this.progress,this.hass&&(0,c.d)(this.hass.locale)):r.s6,!this.progress,this.progress?this.progress/100:void 0):(0,r.qy)(_||(_=x`<label
            for=${0}
            class="container ${0}"
            @drop=${0}
            @dragenter=${0}
            @dragover=${0}
            @dragleave=${0}
            @dragend=${0}
            >${0}
            <input
              id="input"
              type="file"
              class="file"
              .accept=${0}
              .multiple=${0}
              @change=${0}
          /></label>`),this.value?"":"input",(0,l.H)({dragged:this._drag,multiple:this.multiple,value:Boolean(this.value)}),this._handleDrop,this._handleDragStart,this._handleDragStart,this._handleDragEnd,this._handleDragEnd,this.value?"string"==typeof this.value?(0,r.qy)(y||(y=x`<div class="row">
                    <div class="value" @click=${0}>
                      <ha-svg-icon
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </div>
                    <ha-icon-button
                      @click=${0}
                      .label=${0}
                      .path=${0}
                    ></ha-icon-button>
                  </div>`),this._openFilePicker,this.icon||k,this.value,this._clearValue,this.deleteLabel||e("ui.common.delete"),M):(this.value instanceof FileList?Array.from(this.value):(0,p.e)(this.value)).map((t=>(0,r.qy)(b||(b=x`<div class="row">
                        <div class="value" @click=${0}>
                          <ha-svg-icon
                            .path=${0}
                          ></ha-svg-icon>
                          ${0} - ${0}
                        </div>
                        <ha-icon-button
                          @click=${0}
                          .label=${0}
                          .path=${0}
                        ></ha-icon-button>
                      </div>`),this._openFilePicker,this.icon||k,t.name,(0,h.A)(t.size),this._clearValue,this.deleteLabel||e("ui.common.delete"),M))):(0,r.qy)(f||(f=x`<ha-button
                    size="small"
                    appearance="filled"
                    @click=${0}
                  >
                    <ha-svg-icon
                      slot="start"
                      .path=${0}
                    ></ha-svg-icon>
                    ${0}
                  </ha-button>
                  <span class="secondary"
                    >${0}</span
                  >
                  <span class="supports">${0}</span>`),this._openFilePicker,this.icon||k,this.label||e("ui.components.file-upload.label"),this.secondary||e("ui.components.file-upload.secondary"),this.supports),this.accept,this.multiple,this._handleFilePicked))}_openFilePicker(){var e;null===(e=this._input)||void 0===e||e.click()}_handleDrop(e){var t;e.preventDefault(),e.stopPropagation(),null!==(t=e.dataTransfer)&&void 0!==t&&t.files&&(0,n.r)(this,"file-picked",{files:this.multiple||1===e.dataTransfer.files.length?Array.from(e.dataTransfer.files):[e.dataTransfer.files[0]]}),this._drag=!1}_handleDragStart(e){e.preventDefault(),e.stopPropagation(),this._drag=!0}_handleDragEnd(e){e.preventDefault(),e.stopPropagation(),this._drag=!1}_handleFilePicked(e){0!==e.target.files.length&&(this.value=e.target.files,(0,n.r)(this,"file-picked",{files:e.target.files}))}_clearValue(e){e.preventDefault(),this._input.value="",this.value=void 0,(0,n.r)(this,"change"),(0,n.r)(this,"files-cleared")}constructor(...e){super(...e),this.multiple=!1,this.disabled=!1,this.uploading=!1,this.autoOpenFileDialog=!1,this._drag=!1}}w.styles=(0,r.AH)($||($=x`
    :host {
      display: block;
      height: 240px;
    }
    :host([disabled]) {
      pointer-events: none;
      color: var(--disabled-text-color);
    }
    .container {
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      border: solid 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      border-radius: var(--mdc-shape-small, 4px);
      height: 100%;
    }
    .row {
      display: flex;
      align-items: center;
    }
    label.container {
      border: dashed 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      cursor: pointer;
    }
    .container .uploading {
      display: flex;
      flex-direction: column;
      width: 100%;
      align-items: flex-start;
      padding: 0 32px;
      box-sizing: border-box;
    }
    :host([disabled]) .container {
      border-color: var(--disabled-color);
    }
    label:hover,
    label.dragged {
      border-style: solid;
    }
    label.dragged {
      border-color: var(--primary-color);
    }
    .dragged:before {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      background-color: var(--primary-color);
      content: "";
      opacity: var(--dark-divider-opacity);
      pointer-events: none;
      border-radius: var(--mdc-shape-small, 4px);
    }
    label.value {
      cursor: default;
    }
    label.value.multiple {
      justify-content: unset;
      overflow: auto;
    }
    .highlight {
      color: var(--primary-color);
    }
    ha-button {
      margin-bottom: 8px;
    }
    .supports {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }
    :host([disabled]) .secondary {
      color: var(--disabled-text-color);
    }
    input.file {
      display: none;
    }
    .value {
      cursor: pointer;
    }
    .value ha-svg-icon {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
    ha-button {
      --mdc-button-outline-color: var(--primary-color);
      --mdc-icon-button-size: 24px;
    }
    mwc-linear-progress {
      width: 100%;
      padding: 8px 32px;
      box-sizing: border-box;
    }
    .header {
      font-weight: var(--ha-font-weight-medium);
    }
    .progress {
      color: var(--secondary-text-color);
    }
    button.link {
      background: none;
      border: none;
      padding: 0;
      font-size: var(--ha-font-size-m);
      color: var(--primary-color);
      text-decoration: underline;
      cursor: pointer;
    }
  `)),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],w.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],w.prototype,"localize",void 0),(0,a.__decorate)([(0,s.MZ)()],w.prototype,"accept",void 0),(0,a.__decorate)([(0,s.MZ)()],w.prototype,"icon",void 0),(0,a.__decorate)([(0,s.MZ)()],w.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],w.prototype,"secondary",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"uploading-label"})],w.prototype,"uploadingLabel",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"delete-label"})],w.prototype,"deleteLabel",void 0),(0,a.__decorate)([(0,s.MZ)()],w.prototype,"supports",void 0),(0,a.__decorate)([(0,s.MZ)({type:Object})],w.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],w.prototype,"multiple",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],w.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],w.prototype,"uploading",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],w.prototype,"progress",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,attribute:"auto-open-file-dialog"})],w.prototype,"autoOpenFileDialog",void 0),(0,a.__decorate)([(0,s.wk)()],w.prototype,"_drag",void 0),(0,a.__decorate)([(0,s.P)("#input")],w.prototype,"_input",void 0),w=(0,a.__decorate)([(0,s.EM)("ha-file-upload")],w),t()}catch(g){t(g)}}))},7119:function(e,t,i){i.a(e,(async function(e,t){try{i(79827),i(35748),i(5934),i(47849),i(95013);var a=i(69868),o=i(84922),r=i(11991),s=i(73120),l=i(83566),n=i(56082),d=i(47420),c=i(12487),p=i(76943),h=i(81571),u=i(35616),g=e([p,h]);[p,h]=g.then?(await g)():g;let v,m,_,f,y,b=e=>e;const $="M18 15V18H15V20H18V23H20V20H23V18H20V15H18M13.3 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H19C20.1 3 21 3.9 21 5V13.3C20.4 13.1 19.7 13 19 13C17.9 13 16.8 13.3 15.9 13.9L14.5 12L11 16.5L8.5 13.5L5 18H13.1C13 18.3 13 18.7 13 19C13 19.7 13.1 20.4 13.3 21Z";class x extends o.WF{render(){if(!this.value){const e=this.secondary||(this.selectMedia?(0,o.qy)(v||(v=b`${0}`),this.hass.localize("ui.components.picture-upload.secondary",{select_media:(0,o.qy)(m||(m=b`<button
                  class="link"
                  @click=${0}
                >
                  ${0}
                </button>`),this._chooseMedia,this.hass.localize("ui.components.picture-upload.select_media"))})):void 0);return(0,o.qy)(_||(_=b`
        <ha-file-upload
          .hass=${0}
          .icon=${0}
          .label=${0}
          .secondary=${0}
          .supports=${0}
          .uploading=${0}
          @file-picked=${0}
          @change=${0}
          accept="image/png, image/jpeg, image/gif"
        ></ha-file-upload>
      `),this.hass,$,this.label||this.hass.localize("ui.components.picture-upload.label"),e,this.supports||this.hass.localize("ui.components.picture-upload.supported_formats"),this._uploading,this._handleFilePicked,this._handleFileCleared)}return(0,o.qy)(f||(f=b`<div class="center-vertical">
      <div class="value">
        <img
          .src=${0}
          alt=${0}
        />
        <div>
          <ha-button
            appearance="plain"
            size="small"
            variant="danger"
            @click=${0}
          >
            ${0}
          </ha-button>
        </div>
      </div>
    </div>`),this.value,this.currentImageAltText||this.hass.localize("ui.components.picture-upload.current_image_alt"),this._handleChangeClick,this.hass.localize("ui.components.picture-upload.clear_picture"))}_handleChangeClick(){this.value=null,(0,s.r)(this,"change")}async _handleFilePicked(e){const t=e.detail.files[0];this.crop?this._cropFile(t):this._uploadFile(t)}async _handleFileCleared(){this.value=null}async _cropFile(e,t){["image/png","image/jpeg","image/gif"].includes(e.type)?(0,c.Q)(this,{file:e,options:this.cropOptions||{round:!1,aspectRatio:NaN},croppedCallback:i=>{t&&i===e?(this.value=(0,n.Q0)(t,this.size,this.original),(0,s.r)(this,"change")):this._uploadFile(i)}}):(0,d.K$)(this,{text:this.hass.localize("ui.components.picture-upload.unsupported_format")})}async _uploadFile(e){if(["image/png","image/jpeg","image/gif"].includes(e.type)){this._uploading=!0;try{const t=await(0,n.mF)(this.hass,e);this.value=(0,n.Q0)(t.id,this.size,this.original),(0,s.r)(this,"change")}catch(t){(0,d.K$)(this,{text:t.toString()})}finally{this._uploading=!1}}else(0,d.K$)(this,{text:this.hass.localize("ui.components.picture-upload.unsupported_format")})}static get styles(){return[l.RF,(0,o.AH)(y||(y=b`
        :host {
          display: block;
          height: 240px;
        }
        ha-file-upload {
          height: 100%;
        }
        .center-vertical {
          display: flex;
          align-items: center;
          height: 100%;
        }
        .value {
          width: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        img {
          max-width: 100%;
          max-height: 200px;
          margin-bottom: 4px;
          border-radius: var(--file-upload-image-border-radius);
          transition: opacity 0.3s;
          opacity: var(--picture-opacity, 1);
        }
        img:hover {
          opacity: 1;
        }
      `))]}constructor(...e){super(...e),this.value=null,this.crop=!1,this.selectMedia=!1,this.original=!1,this.size=512,this._uploading=!1,this._chooseMedia=()=>{(0,u.O)(this,{action:"pick",entityId:"browser",navigateIds:[{media_content_id:void 0,media_content_type:void 0},{media_content_id:n.AP,media_content_type:"app"}],minimumNavigateLevel:2,mediaPickedCallback:async e=>{const t=(0,n.pD)(e.item.media_content_id);if(t)if(this.crop){const a=(0,n.Q0)(t,void 0,!0);let o;try{o=await(0,n.M5)(this.hass,a)}catch(i){return void(0,d.K$)(this,{text:i.toString()})}const r={type:e.item.media_content_type},s=new File([o],e.item.title,r);this._cropFile(s,t)}else this.value=(0,n.Q0)(t,this.size,this.original),(0,s.r)(this,"change")}})}}}(0,a.__decorate)([(0,r.MZ)()],x.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],x.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)()],x.prototype,"secondary",void 0),(0,a.__decorate)([(0,r.MZ)()],x.prototype,"supports",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],x.prototype,"currentImageAltText",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],x.prototype,"crop",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,attribute:"select-media"})],x.prototype,"selectMedia",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],x.prototype,"cropOptions",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],x.prototype,"original",void 0),(0,a.__decorate)([(0,r.MZ)({type:Number})],x.prototype,"size",void 0),(0,a.__decorate)([(0,r.wk)()],x.prototype,"_uploading",void 0),x=(0,a.__decorate)([(0,r.EM)("ha-picture-upload")],x),t()}catch(v){t(v)}}))},35616:function(e,t,i){i.d(t,{O:function(){return o}});i(35748),i(5934),i(95013);var a=i(73120);const o=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"dialog-media-player-browse",dialogImport:()=>Promise.all([i.e("1629"),i.e("615"),i.e("2087"),i.e("7951"),i.e("5393")]).then(i.bind(i,83e3)),dialogParams:t})}},56082:function(e,t,i){i.d(t,{AP:function(){return o},M5:function(){return d},Q0:function(){return s},fO:function(){return a},mF:function(){return l},pD:function(){return r},vS:function(){return n}});i(46852),i(12977),i(5934),i(56660);const a="/api/image/serve/",o="media-source://image_upload",r=e=>{let t;if(e.startsWith(a)){t=e.substring(a.length);const i=t.indexOf("/");i>=0&&(t=t.substring(0,i))}else e.startsWith(o)&&(t=e.substring(o.length+1));return t},s=(e,t,i=!1)=>{if(!i&&!t)throw new Error("Size must be provided if original is false");return i?`/api/image/serve/${e}/original`:`/api/image/serve/${e}/${t}x${t}`},l=async(e,t)=>{const i=new FormData;i.append("file",t);const a=await e.fetchWithAuth("/api/image/upload",{method:"POST",body:i});if(413===a.status)throw new Error(`Uploaded image is too large (${t.name})`);if(200!==a.status)throw new Error("Unknown error");return a.json()},n=(e,t)=>e.callWS({type:"image/delete",image_id:t}),d=async(e,t)=>{const i=await fetch(e.hassUrl(t));if(!i.ok)throw new Error(`Failed to fetch image: ${i.statusText?i.statusText:i.status}`);return i.blob()}},12487:function(e,t,i){i.d(t,{Q:function(){return r}});i(35748),i(5934),i(95013);var a=i(73120);const o=()=>Promise.all([i.e("2855"),i.e("7328")]).then(i.bind(i,90483)),r=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"image-cropper-dialog",dialogImport:o,dialogParams:t})}},88234:function(e,t,i){i.d(t,{A:function(){return a}});i(92344),i(91455);const a=(e=0,t=2)=>{if(0===e)return"0 Bytes";t=t<0?0:t;const i=Math.floor(Math.log(e)/Math.log(1024));return`${parseFloat((e/1024**i).toFixed(t))} ${["Bytes","KB","MB","GB","TB","PB","EB","ZB","YB"][i]}`}}}]);
//# sourceMappingURL=1092.92af2e56a7c4c0cd.js.map
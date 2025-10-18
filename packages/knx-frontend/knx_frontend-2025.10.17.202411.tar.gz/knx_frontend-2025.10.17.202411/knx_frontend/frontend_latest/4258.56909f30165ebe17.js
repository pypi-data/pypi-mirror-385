export const __webpack_id__="4258";export const __webpack_ids__=["4258"];export const __webpack_modules__={36615:function(t,e,i){var o=i(69868),a=i(84922),s=i(11991),n=i(13802),r=i(73120),d=i(20674);i(93672),i(20014),i(25223),i(37207),i(11934);class l extends a.WF{render(){return a.qy`
      ${this.label?a.qy`<label>${this.label}${this.required?" *":""}</label>`:a.s6}
      <div class="time-input-wrap-wrap">
        <div class="time-input-wrap">
          ${this.enableDay?a.qy`
                <ha-textfield
                  id="day"
                  type="number"
                  inputmode="numeric"
                  .value=${this.days.toFixed()}
                  .label=${this.dayLabel}
                  name="days"
                  @change=${this._valueChanged}
                  @focusin=${this._onFocus}
                  no-spinner
                  .required=${this.required}
                  .autoValidate=${this.autoValidate}
                  min="0"
                  .disabled=${this.disabled}
                  suffix=":"
                  class="hasSuffix"
                >
                </ha-textfield>
              `:a.s6}

          <ha-textfield
            id="hour"
            type="number"
            inputmode="numeric"
            .value=${this.hours.toFixed()}
            .label=${this.hourLabel}
            name="hours"
            @change=${this._valueChanged}
            @focusin=${this._onFocus}
            no-spinner
            .required=${this.required}
            .autoValidate=${this.autoValidate}
            maxlength="2"
            max=${(0,n.J)(this._hourMax)}
            min="0"
            .disabled=${this.disabled}
            suffix=":"
            class="hasSuffix"
          >
          </ha-textfield>
          <ha-textfield
            id="min"
            type="number"
            inputmode="numeric"
            .value=${this._formatValue(this.minutes)}
            .label=${this.minLabel}
            @change=${this._valueChanged}
            @focusin=${this._onFocus}
            name="minutes"
            no-spinner
            .required=${this.required}
            .autoValidate=${this.autoValidate}
            maxlength="2"
            max="59"
            min="0"
            .disabled=${this.disabled}
            .suffix=${this.enableSecond?":":""}
            class=${this.enableSecond?"has-suffix":""}
          >
          </ha-textfield>
          ${this.enableSecond?a.qy`<ha-textfield
                id="sec"
                type="number"
                inputmode="numeric"
                .value=${this._formatValue(this.seconds)}
                .label=${this.secLabel}
                @change=${this._valueChanged}
                @focusin=${this._onFocus}
                name="seconds"
                no-spinner
                .required=${this.required}
                .autoValidate=${this.autoValidate}
                maxlength="2"
                max="59"
                min="0"
                .disabled=${this.disabled}
                .suffix=${this.enableMillisecond?":":""}
                class=${this.enableMillisecond?"has-suffix":""}
              >
              </ha-textfield>`:a.s6}
          ${this.enableMillisecond?a.qy`<ha-textfield
                id="millisec"
                type="number"
                .value=${this._formatValue(this.milliseconds,3)}
                .label=${this.millisecLabel}
                @change=${this._valueChanged}
                @focusin=${this._onFocus}
                name="milliseconds"
                no-spinner
                .required=${this.required}
                .autoValidate=${this.autoValidate}
                maxlength="3"
                max="999"
                min="0"
                .disabled=${this.disabled}
              >
              </ha-textfield>`:a.s6}
          ${!this.clearable||this.required||this.disabled?a.s6:a.qy`<ha-icon-button
                label="clear"
                @click=${this._clearValue}
                .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              ></ha-icon-button>`}
        </div>

        ${24===this.format?a.s6:a.qy`<ha-select
              .required=${this.required}
              .value=${this.amPm}
              .disabled=${this.disabled}
              name="amPm"
              naturalMenuWidth
              fixedMenuPosition
              @selected=${this._valueChanged}
              @closed=${d.d}
            >
              <ha-list-item value="AM">AM</ha-list-item>
              <ha-list-item value="PM">PM</ha-list-item>
            </ha-select>`}
      </div>
      ${this.helper?a.qy`<ha-input-helper-text .disabled=${this.disabled}
            >${this.helper}</ha-input-helper-text
          >`:a.s6}
    `}_clearValue(){(0,r.r)(this,"value-changed")}_valueChanged(t){const e=t.currentTarget;this[e.name]="amPm"===e.name?e.value:Number(e.value);const i={hours:this.hours,minutes:this.minutes,seconds:this.seconds,milliseconds:this.milliseconds};this.enableDay&&(i.days=this.days),12===this.format&&(i.amPm=this.amPm),(0,r.r)(this,"value-changed",{value:i})}_onFocus(t){t.currentTarget.select()}_formatValue(t,e=2){return t.toString().padStart(e,"0")}get _hourMax(){if(!this.noHoursLimit)return 12===this.format?12:23}constructor(...t){super(...t),this.autoValidate=!1,this.required=!1,this.format=12,this.disabled=!1,this.days=0,this.hours=0,this.minutes=0,this.seconds=0,this.milliseconds=0,this.dayLabel="",this.hourLabel="",this.minLabel="",this.secLabel="",this.millisecLabel="",this.enableSecond=!1,this.enableMillisecond=!1,this.enableDay=!1,this.noHoursLimit=!1,this.amPm="AM"}}l.styles=a.AH`
    :host([clearable]) {
      position: relative;
    }
    .time-input-wrap-wrap {
      display: flex;
    }
    .time-input-wrap {
      display: flex;
      flex: var(--time-input-flex, unset);
      border-radius: var(--mdc-shape-small, 4px) var(--mdc-shape-small, 4px) 0 0;
      overflow: hidden;
      position: relative;
      direction: ltr;
      padding-right: 3px;
    }
    ha-textfield {
      width: 60px;
      flex-grow: 1;
      text-align: center;
      --mdc-shape-small: 0;
      --text-field-appearance: none;
      --text-field-padding: 0 4px;
      --text-field-suffix-padding-left: 2px;
      --text-field-suffix-padding-right: 0;
      --text-field-text-align: center;
    }
    ha-textfield.hasSuffix {
      --text-field-padding: 0 0 0 4px;
    }
    ha-textfield:first-child {
      --text-field-border-top-left-radius: var(--mdc-shape-medium);
    }
    ha-textfield:last-child {
      --text-field-border-top-right-radius: var(--mdc-shape-medium);
    }
    ha-select {
      --mdc-shape-small: 0;
      width: 85px;
    }
    :host([clearable]) .mdc-select__anchor {
      padding-inline-end: var(--select-selected-text-padding-end, 12px);
    }
    ha-icon-button {
      position: relative;
      --mdc-icon-button-size: 36px;
      --mdc-icon-size: 20px;
      color: var(--secondary-text-color);
      direction: var(--direction);
      display: flex;
      align-items: center;
      background-color: var(--mdc-text-field-fill-color, whitesmoke);
      border-bottom-style: solid;
      border-bottom-width: 1px;
    }
    label {
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      -webkit-font-smoothing: var(--ha-font-smoothing);
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, var(--ha-font-family-body))
      );
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      line-height: var(
        --mdc-typography-body2-line-height,
        var(--ha-line-height-condensed)
      );
      font-weight: var(
        --mdc-typography-body2-font-weight,
        var(--ha-font-weight-normal)
      );
      letter-spacing: var(
        --mdc-typography-body2-letter-spacing,
        0.0178571429em
      );
      text-decoration: var(--mdc-typography-body2-text-decoration, inherit);
      text-transform: var(--mdc-typography-body2-text-transform, inherit);
      color: var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87));
      padding-left: 4px;
      padding-inline-start: 4px;
      padding-inline-end: initial;
    }
    ha-input-helper-text {
      padding-top: 8px;
      line-height: var(--ha-line-height-condensed);
    }
  `,(0,o.__decorate)([(0,s.MZ)()],l.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)()],l.prototype,"helper",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"auto-validate",type:Boolean})],l.prototype,"autoValidate",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],l.prototype,"required",void 0),(0,o.__decorate)([(0,s.MZ)({type:Number})],l.prototype,"format",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],l.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({type:Number})],l.prototype,"days",void 0),(0,o.__decorate)([(0,s.MZ)({type:Number})],l.prototype,"hours",void 0),(0,o.__decorate)([(0,s.MZ)({type:Number})],l.prototype,"minutes",void 0),(0,o.__decorate)([(0,s.MZ)({type:Number})],l.prototype,"seconds",void 0),(0,o.__decorate)([(0,s.MZ)({type:Number})],l.prototype,"milliseconds",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"day-label"})],l.prototype,"dayLabel",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"hour-label"})],l.prototype,"hourLabel",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"min-label"})],l.prototype,"minLabel",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"sec-label"})],l.prototype,"secLabel",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"ms-label"})],l.prototype,"millisecLabel",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"enable-second",type:Boolean})],l.prototype,"enableSecond",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"enable-millisecond",type:Boolean})],l.prototype,"enableMillisecond",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"enable-day",type:Boolean})],l.prototype,"enableDay",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"no-hours-limit",type:Boolean})],l.prototype,"noHoursLimit",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"amPm",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],l.prototype,"clearable",void 0),l=(0,o.__decorate)([(0,s.EM)("ha-base-time-input")],l)},76450:function(t,e,i){var o=i(69868),a=i(84922),s=i(11991),n=i(73120);i(36615);class r extends a.WF{render(){return a.qy`
      <ha-base-time-input
        .label=${this.label}
        .helper=${this.helper}
        .required=${this.required}
        .clearable=${!this.required&&void 0!==this.data}
        .autoValidate=${this.required}
        .disabled=${this.disabled}
        errorMessage="Required"
        enable-second
        .enableMillisecond=${this.enableMillisecond}
        .enableDay=${this.enableDay}
        format="24"
        .days=${this._days}
        .hours=${this._hours}
        .minutes=${this._minutes}
        .seconds=${this._seconds}
        .milliseconds=${this._milliseconds}
        @value-changed=${this._durationChanged}
        no-hours-limit
        day-label="dd"
        hour-label="hh"
        min-label="mm"
        sec-label="ss"
        ms-label="ms"
      ></ha-base-time-input>
    `}get _days(){return this.data?.days?Number(this.data.days):this.required||this.data?0:NaN}get _hours(){return this.data?.hours?Number(this.data.hours):this.required||this.data?0:NaN}get _minutes(){return this.data?.minutes?Number(this.data.minutes):this.required||this.data?0:NaN}get _seconds(){return this.data?.seconds?Number(this.data.seconds):this.required||this.data?0:NaN}get _milliseconds(){return this.data?.milliseconds?Number(this.data.milliseconds):this.required||this.data?0:NaN}_durationChanged(t){t.stopPropagation();const e=t.detail.value?{...t.detail.value}:void 0;e&&(e.hours||=0,e.minutes||=0,e.seconds||=0,"days"in e&&(e.days||=0),"milliseconds"in e&&(e.milliseconds||=0),this.enableMillisecond||e.milliseconds?e.milliseconds>999&&(e.seconds+=Math.floor(e.milliseconds/1e3),e.milliseconds%=1e3):delete e.milliseconds,e.seconds>59&&(e.minutes+=Math.floor(e.seconds/60),e.seconds%=60),e.minutes>59&&(e.hours+=Math.floor(e.minutes/60),e.minutes%=60),this.enableDay&&e.hours>24&&(e.days=(e.days??0)+Math.floor(e.hours/24),e.hours%=24)),(0,n.r)(this,"value-changed",{value:e})}constructor(...t){super(...t),this.required=!1,this.enableMillisecond=!1,this.enableDay=!1,this.disabled=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"data",void 0),(0,o.__decorate)([(0,s.MZ)()],r.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)()],r.prototype,"helper",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],r.prototype,"required",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"enable-millisecond",type:Boolean})],r.prototype,"enableMillisecond",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"enable-day",type:Boolean})],r.prototype,"enableDay",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],r.prototype,"disabled",void 0),r=(0,o.__decorate)([(0,s.EM)("ha-duration-input")],r)},31257:function(t,e,i){i.a(t,(async function(t,o){try{i.r(e),i.d(e,{HaActionSelector:()=>m});var a=i(69868),s=i(97809),n=i(84922),r=i(11991),d=i(65940),l=i(24986),c=i(2834),h=i(17866),p=i(4331),u=i(32020),_=t([u]);u=(_.then?(await _)():_)[0];class m extends((0,p.E)(n.WF)){firstUpdated(){this._entityReg||(this._entitiesContext=new s.DT(this,{context:l.ih,initialValue:[]}))}hassSubscribe(){return[(0,c.Bz)(this.hass.connection,(t=>{this._entitiesContext.setValue(t)}))]}expandAll(){this._actionElement?.expandAll()}collapseAll(){this._actionElement?.collapseAll()}render(){return n.qy`
      ${this.label?n.qy`<label>${this.label}</label>`:n.s6}
      <ha-automation-action
        .disabled=${this.disabled}
        .actions=${this._actions(this.value)}
        .hass=${this.hass}
        .narrow=${this.narrow}
        .optionsInSidebar=${!!this.selector.action?.optionsInSidebar}
      ></ha-automation-action>
    `}constructor(...t){super(...t),this.narrow=!1,this.disabled=!1,this.hassSubscribeRequiredHostProps=["_entitiesContext"],this._actions=(0,d.A)((t=>t?(0,h.Rn)(t):[]))}}m.styles=n.AH`
    ha-automation-action {
      display: block;
    }
    label {
      display: block;
      margin-bottom: 4px;
      font-weight: var(--ha-font-weight-medium);
      color: var(--secondary-text-color);
    }
  `,(0,a.__decorate)([(0,r.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],m.prototype,"narrow",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],m.prototype,"selector",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],m.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],m.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],m.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.wk)(),(0,s.Fg)({context:l.ih,subscribe:!0})],m.prototype,"_entityReg",void 0),(0,a.__decorate)([(0,r.wk)()],m.prototype,"_entitiesContext",void 0),(0,a.__decorate)([(0,r.P)("ha-automation-action")],m.prototype,"_actionElement",void 0),m=(0,a.__decorate)([(0,r.EM)("ha-selector-action")],m),o()}catch(m){o(m)}}))},95475:function(t,e,i){i.d(e,{I8:()=>p,L_:()=>h,MC:()=>c,O$:()=>a,_c:()=>n,cQ:()=>l,ix:()=>s,kd:()=>d,ts:()=>r});const o="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z",a={condition:"M4 2A2 2 0 0 0 2 4V12H4V8H6V12H8V4A2 2 0 0 0 6 2H4M4 4H6V6H4M22 15.5V14A2 2 0 0 0 20 12H16V22H20A2 2 0 0 0 22 20V18.5A1.54 1.54 0 0 0 20.5 17A1.54 1.54 0 0 0 22 15.5M20 20H18V18H20V20M20 16H18V14H20M5.79 21.61L4.21 20.39L18.21 2.39L19.79 3.61Z",delay:"M12,20A7,7 0 0,1 5,13A7,7 0 0,1 12,6A7,7 0 0,1 19,13A7,7 0 0,1 12,20M19.03,7.39L20.45,5.97C20,5.46 19.55,5 19.04,4.56L17.62,6C16.07,4.74 14.12,4 12,4A9,9 0 0,0 3,13A9,9 0 0,0 12,22C17,22 21,17.97 21,13C21,10.88 20.26,8.93 19.03,7.39M11,14H13V8H11M15,1H9V3H15V1Z",event:"M10,9A1,1 0 0,1 11,8A1,1 0 0,1 12,9V13.47L13.21,13.6L18.15,15.79C18.68,16.03 19,16.56 19,17.14V21.5C18.97,22.32 18.32,22.97 17.5,23H11C10.62,23 10.26,22.85 10,22.57L5.1,18.37L5.84,17.6C6.03,17.39 6.3,17.28 6.58,17.28H6.8L10,19V9M11,5A4,4 0 0,1 15,9C15,10.5 14.2,11.77 13,12.46V11.24C13.61,10.69 14,9.89 14,9A3,3 0 0,0 11,6A3,3 0 0,0 8,9C8,9.89 8.39,10.69 9,11.24V12.46C7.8,11.77 7,10.5 7,9A4,4 0 0,1 11,5M11,3A6,6 0 0,1 17,9C17,10.7 16.29,12.23 15.16,13.33L14.16,12.88C15.28,11.96 16,10.56 16,9A5,5 0 0,0 11,4A5,5 0 0,0 6,9C6,11.05 7.23,12.81 9,13.58V14.66C6.67,13.83 5,11.61 5,9A6,6 0 0,1 11,3Z",play_media:"M8,5.14V19.14L19,12.14L8,5.14Z",service:"M12,5A2,2 0 0,1 14,7C14,7.24 13.96,7.47 13.88,7.69C17.95,8.5 21,11.91 21,16H3C3,11.91 6.05,8.5 10.12,7.69C10.04,7.47 10,7.24 10,7A2,2 0 0,1 12,5M22,19H2V17H22V19Z",wait_template:"M8,3A2,2 0 0,0 6,5V9A2,2 0 0,1 4,11H3V13H4A2,2 0 0,1 6,15V19A2,2 0 0,0 8,21H10V19H8V14A2,2 0 0,0 6,12A2,2 0 0,0 8,10V5H10V3M16,3A2,2 0 0,1 18,5V9A2,2 0 0,0 20,11H21V13H20A2,2 0 0,0 18,15V19A2,2 0 0,1 16,21H14V19H16V14A2,2 0 0,1 18,12A2,2 0 0,1 16,10V5H14V3H16Z",wait_for_trigger:"M12,9A2,2 0 0,1 10,7C10,5.89 10.9,5 12,5C13.11,5 14,5.89 14,7A2,2 0 0,1 12,9M12,14A2,2 0 0,1 10,12C10,10.89 10.9,10 12,10C13.11,10 14,10.89 14,12A2,2 0 0,1 12,14M12,19A2,2 0 0,1 10,17C10,15.89 10.9,15 12,15C13.11,15 14,15.89 14,17A2,2 0 0,1 12,19M20,10H17V8.86C18.72,8.41 20,6.86 20,5H17V4A1,1 0 0,0 16,3H8A1,1 0 0,0 7,4V5H4C4,6.86 5.28,8.41 7,8.86V10H4C4,11.86 5.28,13.41 7,13.86V15H4C4,16.86 5.28,18.41 7,18.86V20A1,1 0 0,0 8,21H16A1,1 0 0,0 17,20V18.86C18.72,18.41 20,16.86 20,15H17V13.86C18.72,13.41 20,11.86 20,10Z",repeat:o,repeat_count:o,repeat_while:o,repeat_until:o,repeat_for_each:o,choose:"M11,5H8L12,1L16,5H13V9.43C12.25,9.89 11.58,10.46 11,11.12V5M22,11L18,7V10C14.39,9.85 11.31,12.57 11,16.17C9.44,16.72 8.62,18.44 9.17,20C9.72,21.56 11.44,22.38 13,21.83C14.56,21.27 15.38,19.56 14.83,18C14.53,17.14 13.85,16.47 13,16.17C13.47,12.17 17.47,11.97 17.95,11.97V14.97L22,11M10.63,11.59C9.3,10.57 7.67,10 6,10V7L2,11L6,15V12C7.34,12.03 8.63,12.5 9.64,13.4C9.89,12.76 10.22,12.15 10.63,11.59Z",if:"M14,4L16.29,6.29L13.41,9.17L14.83,10.59L17.71,7.71L20,10V4M10,4H4V10L6.29,7.71L11,12.41V20H13V11.59L7.71,6.29",device_id:"M3 6H21V4H3C1.9 4 1 4.9 1 6V18C1 19.1 1.9 20 3 20H7V18H3V6M13 12H9V13.78C8.39 14.33 8 15.11 8 16C8 16.89 8.39 17.67 9 18.22V20H13V18.22C13.61 17.67 14 16.88 14 16S13.61 14.33 13 13.78V12M11 17.5C10.17 17.5 9.5 16.83 9.5 16S10.17 14.5 11 14.5 12.5 15.17 12.5 16 11.83 17.5 11 17.5M22 8H16C15.5 8 15 8.5 15 9V19C15 19.5 15.5 20 16 20H22C22.5 20 23 19.5 23 19V9C23 8.5 22.5 8 22 8M21 18H17V10H21V18Z",stop:"M13 24C9.74 24 6.81 22 5.6 19L2.57 11.37C2.26 10.58 3 9.79 3.81 10.05L4.6 10.31C5.16 10.5 5.62 10.92 5.84 11.47L7.25 15H8V3.25C8 2.56 8.56 2 9.25 2S10.5 2.56 10.5 3.25V12H11.5V1.25C11.5 .56 12.06 0 12.75 0S14 .56 14 1.25V12H15V2.75C15 2.06 15.56 1.5 16.25 1.5C16.94 1.5 17.5 2.06 17.5 2.75V12H18.5V5.75C18.5 5.06 19.06 4.5 19.75 4.5S21 5.06 21 5.75V16C21 20.42 17.42 24 13 24Z",sequence:"M7,13V11H21V13H7M7,19V17H21V19H7M7,7V5H21V7H7M3,8V5H2V4H4V8H3M2,17V16H5V20H2V19H4V18.5H3V17.5H4V17H2M4.25,10A0.75,0.75 0 0,1 5,10.75C5,10.95 4.92,11.14 4.79,11.27L3.12,13H5V14H2V13.08L4,11H2V10H4.25Z",parallel:"M16,4.5V7H5V9H16V11.5L19.5,8M16,12.5V15H5V17H16V19.5L19.5,16",variables:"M21 2H3C1.9 2 1 2.9 1 4V20C1 21.1 1.9 22 3 22H21C22.1 22 23 21.1 23 20V4C23 2.9 22.1 2 21 2M21 20H3V6H21V20M16.6 8C18.1 9.3 19 11.1 19 13C19 14.9 18.1 16.7 16.6 18L15 17.4C16.3 16.4 17 14.7 17 13S16.3 9.6 15 8.6L16.6 8M7.4 8L9 8.6C7.7 9.6 7 11.3 7 13S7.7 16.4 9 17.4L7.4 18C5.9 16.7 5 14.9 5 13S5.9 9.3 7.4 8M12.1 12L13.5 10H15L12.8 13L14.1 16H12.8L12 14L10.6 16H9L11.3 12.9L10 10H11.3L12.1 12Z",set_conversation_response:"M12,8H4A2,2 0 0,0 2,10V14A2,2 0 0,0 4,16H5V20A1,1 0 0,0 6,21H8A1,1 0 0,0 9,20V16H12L17,20V4L12,8M21.5,12C21.5,13.71 20.54,15.26 19,16V8C20.53,8.75 21.5,10.3 21.5,12Z"},s=new Set(["variables"]),n={device_id:{},helpers:{icon:"M21.71 20.29L20.29 21.71A1 1 0 0 1 18.88 21.71L7 9.85A3.81 3.81 0 0 1 6 10A4 4 0 0 1 2.22 4.7L4.76 7.24L5.29 6.71L6.71 5.29L7.24 4.76L4.7 2.22A4 4 0 0 1 10 6A3.81 3.81 0 0 1 9.85 7L21.71 18.88A1 1 0 0 1 21.71 20.29M2.29 18.88A1 1 0 0 0 2.29 20.29L3.71 21.71A1 1 0 0 0 5.12 21.71L10.59 16.25L7.76 13.42M20 2L16 4V6L13.83 8.17L15.83 10.17L18 8H20L22 4Z",members:{}},building_blocks:{icon:"M18.5 18.5C19.04 18.5 19.5 18.96 19.5 19.5S19.04 20.5 18.5 20.5H6.5C5.96 20.5 5.5 20.04 5.5 19.5S5.96 18.5 6.5 18.5H18.5M18.5 17H6.5C5.13 17 4 18.13 4 19.5S5.13 22 6.5 22H18.5C19.88 22 21 20.88 21 19.5S19.88 17 18.5 17M21 11H18V7H13L10 11V16H22L21 11M11.54 11L13.5 8.5H16V11H11.54M9.76 3.41L4.76 2L2 11.83C1.66 13.11 2.41 14.44 3.7 14.8L4.86 15.12L8.15 12.29L4.27 11.21L6.15 4.46L8.94 5.24C9.5 5.53 10.71 6.34 11.47 7.37L12.5 6H12.94C11.68 4.41 9.85 3.46 9.76 3.41Z",members:{condition:{},delay:{},wait_template:{},wait_for_trigger:{},repeat_count:{},repeat_while:{},repeat_until:{},repeat_for_each:{},choose:{},if:{},stop:{},sequence:{},parallel:{},variables:{}}},other:{icon:"M16,12A2,2 0 0,1 18,10A2,2 0 0,1 20,12A2,2 0 0,1 18,14A2,2 0 0,1 16,12M10,12A2,2 0 0,1 12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12M4,12A2,2 0 0,1 6,10A2,2 0 0,1 8,12A2,2 0 0,1 6,14A2,2 0 0,1 4,12Z",members:{event:{},service:{},set_conversation_response:{}}}},r="__SERVICE__",d=t=>t?.startsWith(r),l=t=>t.substring(r.length),c=["ha-automation-action-choose","ha-automation-action-condition","ha-automation-action-if","ha-automation-action-parallel","ha-automation-action-repeat","ha-automation-action-sequence"],h=["choose","if","parallel","sequence","repeat_while","repeat_until"],p=["repeat_count","repeat_for_each","wait_for_trigger"]},73473:function(t,e,i){i.a(t,(async function(t,o){try{i.d(e,{u:()=>b});var a=i(26846),s=i(52744),n=i(15216),r=i(44537),d=i(47379),l=i(72106),c=i(71767),h=i(10101),p=i(7657),u=i(2834),_=i(28027),m=i(17866),v=t([s,l,h]);[s,l,h]=v.then?(await v)():v;const g="ui.panel.config.automation.editor.actions.type",b=(t,e,i,o,a,s,n=!1)=>{try{const r=y(t,e,i,o,a,s,n);if("string"!=typeof r)throw new Error(String(r));return r}catch(r){console.error(r);let t="Error in describing action";return r.message&&(t+=": "+r.message),t}},y=(t,e,i,o,v,b,y=!1)=>{if(v.alias&&!y)return v.alias;if(b||(b=(0,m.pq)(v)),"service"===b){const s=v,n=[],h=s.target||s.data;if("string"==typeof h&&(0,c.F)(h))n.push(t.localize(`${g}.service.description.target_template`,{name:"target"}));else if(h)for(const[l,p]of Object.entries({area_id:"areas",device_id:"devices",entity_id:"entities",floor_id:"floors",label_id:"labels"})){if(!(l in h))continue;const s=(0,a.e)(h[l])||[];for(const a of s){if((0,c.F)(a)){n.push(t.localize(`${g}.service.description.target_template`,{name:p}));break}if("entity_id"===l)if(a.includes(".")){const e=t.states[a];e?n.push((0,d.u)(e)):n.push(a)}else{const i=(0,u.P9)(e)[a];i?n.push((0,u.jh)(t,i)||a):"all"===a?n.push(t.localize(`${g}.service.description.target_every_entity`)):n.push(t.localize(`${g}.service.description.target_unknown_entity`))}else if("device_id"===l){const e=t.devices[a];e?n.push((0,r.T)(e,t)):n.push(t.localize(`${g}.service.description.target_unknown_device`))}else if("area_id"===l){const e=t.areas[a];e?.name?n.push(e.name):n.push(t.localize(`${g}.service.description.target_unknown_area`))}else if("floor_id"===l){const e=o[a]??void 0;e?.name?n.push(e.name):n.push(t.localize(`${g}.service.description.target_unknown_floor`))}else if("label_id"===l){const e=i.find((t=>t.label_id===a));e?.name?n.push(e.name):n.push(t.localize(`${g}.service.description.target_unknown_label`))}else n.push(a)}}if(s.service_template||s.action&&(0,c.F)(s.action))return t.localize(n.length?`${g}.service.description.service_based_on_template`:`${g}.service.description.service_based_on_template_no_targets`,{targets:(0,l.c)(t.locale,n)});if(s.action){const[e,i]=s.action.split(".",2),o=t.localize(`component.${e}.services.${i}.name`)||t.services[e][i]?.name;return s.metadata?t.localize(n.length?`${g}.service.description.service_name`:`${g}.service.description.service_name_no_targets`,{domain:(0,_.p$)(t.localize,e),name:o||s.action,targets:(0,l.c)(t.locale,n)}):t.localize(n.length?`${g}.service.description.service_based_on_name`:`${g}.service.description.service_based_on_name_no_targets`,{name:o?`${(0,_.p$)(t.localize,e)}: ${o}`:s.action,targets:(0,l.c)(t.locale,n)})}return t.localize(`${g}.service.description.service`)}if("delay"===b){const e=v;let i;return i="number"==typeof e.delay?t.localize(`${g}.delay.description.duration_string`,{string:(0,n.A)(e.delay)}):"string"==typeof e.delay?(0,c.F)(e.delay)?t.localize(`${g}.delay.description.duration_template`):t.localize(`${g}.delay.description.duration_string`,{string:e.delay||t.localize(`${g}.delay.description.duration_unknown`)}):e.delay?t.localize(`${g}.delay.description.duration_string`,{string:(0,s.nR)(t.locale,e.delay)}):t.localize(`${g}.delay.description.duration_string`,{string:t.localize(`${g}.delay.description.duration_unknown`)}),t.localize(`${g}.delay.description.full`,{duration:i})}if("wait_for_trigger"===b){const e=v,i=(0,a.e)(e.wait_for_trigger);return i&&0!==i.length?t.localize(`${g}.wait_for_trigger.description.wait_for_triggers`,{count:i.length}):t.localize(`${g}.wait_for_trigger.description.wait_for_a_trigger`)}if("variables"===b){const e=v;return t.localize(`${g}.variables.description.full`,{names:(0,l.c)(t.locale,Object.keys(e.variables))})}if("fire_event"===b){const e=v;return(0,c.F)(e.event)?t.localize(`${g}.event.description.full`,{name:t.localize(`${g}.event.description.template`)}):t.localize(`${g}.event.description.full`,{name:e.event})}if("wait_template"===b)return t.localize(`${g}.wait_template.description.full`);if("stop"===b){const e=v;return t.localize(`${g}.stop.description.full`,{hasReason:void 0!==e.stop?"true":"false",reason:e.stop})}if("if"===b){return void 0!==v.else?t.localize(`${g}.if.description.if_else`):t.localize(`${g}.if.description.if`)}if("choose"===b){const e=v;if(e.choose){const i=(0,a.e)(e.choose).length+(e.default?1:0);return t.localize(`${g}.choose.description.full`,{number:i})}return t.localize(`${g}.choose.description.no_action`)}if("repeat"===b){const e=v;let i="";if("count"in e.repeat){const o=e.repeat.count;i=t.localize(`${g}.repeat.description.count`,{count:o})}else if("while"in e.repeat){const o=(0,a.e)(e.repeat.while);i=t.localize(`${g}.repeat.description.while_count`,{count:o.length})}else if("until"in e.repeat){const o=(0,a.e)(e.repeat.until);i=t.localize(`${g}.repeat.description.until_count`,{count:o.length})}else if("for_each"in e.repeat){const o=(0,a.e)(e.repeat.for_each).map((t=>JSON.stringify(t)));i=t.localize(`${g}.repeat.description.for_each`,{items:(0,l.c)(t.locale,o)})}return t.localize(`${g}.repeat.description.full`,{chosenAction:i})}if("check_condition"===b)return t.localize(`${g}.check_condition.description.full`,{condition:(0,h.p)(v,t,e)});if("device_action"===b){const i=v;if(!i.device_id)return t.localize(`${g}.device_id.description.no_device`);const o=(0,p.PV)(t,e,i);if(o)return o;const a=t.states[i.entity_id];return i.type?`${i.type} ${a?(0,d.u)(a):i.entity_id}`:t.localize(`${g}.device_id.description.perform_device_action`,{device:a?(0,d.u)(a):i.entity_id})}if("sequence"===b){const e=v,i=(0,a.e)(e.sequence).length;return t.localize(`${g}.sequence.description.full`,{number:i})}if("parallel"===b){const e=v,i=(0,a.e)(e.parallel).length;return t.localize(`${g}.parallel.description.full`,{number:i})}if("set_conversation_response"===b){const e=v;return(0,c.F)(e.set_conversation_response)?t.localize(`${g}.set_conversation_response.description.template`):t.localize(`${g}.set_conversation_response.description.full`,{response:e.set_conversation_response})}return b};o()}catch(g){o(g)}}))},34586:function(t,e,i){i.d(e,{d:()=>o});const o=(t,e)=>t.callWS({type:"execute_script",sequence:e})},4331:function(t,e,i){i.d(e,{E:()=>s});var o=i(69868),a=i(11991);const s=t=>{class e extends t{connectedCallback(){super.connectedCallback(),this._checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const t=this.__unsubs.pop();t instanceof Promise?t.then((t=>t())):t()}this.__unsubs=void 0}}updated(t){if(super.updated(t),t.has("hass"))this._checkSubscribed();else if(this.hassSubscribeRequiredHostProps)for(const e of t.keys())if(this.hassSubscribeRequiredHostProps.includes(e))return void this._checkSubscribed()}hassSubscribe(){return[]}_checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&!this.hassSubscribeRequiredHostProps?.some((t=>void 0===this[t]))&&(this.__unsubs=this.hassSubscribe())}}return(0,o.__decorate)([(0,a.MZ)({attribute:!1})],e.prototype,"hass",void 0),e}},4112:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(84922),s=i(11991),n=i(75907),r=i(21431),d=i(73120),l=i(79080),c=i(95475),h=i(17866),p=(i(7245),i(68975)),u=i(18373),_=t([l,u]);[l,u]=_.then?(await _)():_;class m extends a.WF{render(){const t=this.yamlMode||!this.uiSupported,e=(0,u.MS)(this.action);return a.qy`
      <div
        class=${(0,n.H)({"card-content":!0,disabled:!this.indent&&(this.disabled||!1===this.action.enabled&&!this.yamlMode),yaml:t,indent:this.indent,card:!this.inSidebar})}
      >
        ${t?a.qy`
              ${this.uiSupported?a.s6:a.qy`
                    <ha-automation-editor-warning
                      .alertTitle=${this.hass.localize("ui.panel.config.automation.editor.actions.unsupported_action")}
                      .localize=${this.hass.localize}
                    ></ha-automation-editor-warning>
                  `}
              <ha-yaml-editor
                .hass=${this.hass}
                .defaultValue=${this.action}
                @value-changed=${this._onYamlChange}
                .readOnly=${this.disabled}
              ></ha-yaml-editor>
            `:a.qy`
              <div @value-changed=${this._onUiChanged}>
                ${(0,r._)(`ha-automation-action-${e}`,{hass:this.hass,action:this.action,disabled:this.disabled,narrow:this.narrow,optionsInSidebar:this.indent,indent:this.indent,inSidebar:this.inSidebar})}
              </div>
            `}
      </div>
    `}_onYamlChange(t){t.stopPropagation(),t.detail.isValid&&(0,d.r)(this,this.inSidebar?"yaml-changed":"value-changed",{value:(0,h.Rn)(t.detail.value)})}_onUiChanged(t){t.stopPropagation();const e={...this.action.alias?{alias:this.action.alias}:{},...t.detail.value};(0,d.r)(this,"value-changed",{value:e})}expandAll(){this._collapsibleElement?.expandAll?.()}collapseAll(){this._collapsibleElement?.collapseAll?.()}constructor(...t){super(...t),this.disabled=!1,this.yamlMode=!1,this.indent=!1,this.selected=!1,this.narrow=!1,this.inSidebar=!1,this.uiSupported=!1}}m.styles=[p.yj,p.aM],(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],m.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"yamlMode",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],m.prototype,"indent",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],m.prototype,"selected",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],m.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"sidebar"})],m.prototype,"inSidebar",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"supported"})],m.prototype,"uiSupported",void 0),(0,o.__decorate)([(0,s.P)("ha-yaml-editor")],m.prototype,"yamlEditor",void 0),(0,o.__decorate)([(0,s.P)(c.MC.join(", "))],m.prototype,"_collapsibleElement",void 0),m=(0,o.__decorate)([(0,s.EM)("ha-automation-action-editor")],m),e()}catch(m){e(m)}}))},18373:function(t,e,i){i.a(t,(async function(t,o){try{i.d(e,{MS:()=>ot,Pb:()=>at});var a=i(69868),s=i(97809),n=i(97481),r=i(90227),d=i(84922),l=i(11991),c=i(65940),h=i(26846),p=i(83490),u=i(73120),_=i(88727),m=i(20674),v=i(8692),g=i(4071),b=i(5503),y=(i(29897),i(86853),i(99741),i(93672),i(61647),i(90666),i(70154),i(57544)),f=i(89652),$=i(95475),M=i(32588),w=i(88151),A=i(24986),C=i(17866),V=i(73473),x=i(34586),H=i(47420),S=i(52493),L=i(72698),Z=(i(7245),i(68975)),k=i(4112),q=i(44158),z=i(68130),E=(i(12696),i(72011),i(94819)),I=i(25056),P=i(41856),B=i(44392),O=i(52118),D=i(96556),R=(i(99235),i(28975),i(62353)),F=(i(55639),t([y,f,k,q,z,E,I,P,O,D,R,B,V]));[y,f,k,q,z,E,I,P,O,D,R,B,V]=F.then?(await F)():F;const N="M18.75 22.16L16 19.16L17.16 18L18.75 19.59L22.34 16L23.5 17.41L18.75 22.16M13 13V7H11V13H13M13 17V15H11V17H13M12 2C17.5 2 22 6.5 22 12L21.91 13.31C21.31 13.11 20.67 13 20 13C16.69 13 14 15.69 14 19C14 19.95 14.22 20.85 14.62 21.65C13.78 21.88 12.91 22 12 22C6.5 22 2 17.5 2 12C2 6.5 6.5 2 12 2Z",T="M6,2A4,4 0 0,1 10,6V8H14V6A4,4 0 0,1 18,2A4,4 0 0,1 22,6A4,4 0 0,1 18,10H16V14H18A4,4 0 0,1 22,18A4,4 0 0,1 18,22A4,4 0 0,1 14,18V16H10V18A4,4 0 0,1 6,22A4,4 0 0,1 2,18A4,4 0 0,1 6,14H8V10H6A4,4 0 0,1 2,6A4,4 0 0,1 6,2M16,18A2,2 0 0,0 18,20A2,2 0 0,0 20,18A2,2 0 0,0 18,16H16V18M14,10H10V14H14V10M6,16A2,2 0 0,0 4,18A2,2 0 0,0 6,20A2,2 0 0,0 8,18V16H6M8,6A2,2 0 0,0 6,4A2,2 0 0,0 4,6A2,2 0 0,0 6,8H8V6M18,8A2,2 0 0,0 20,6A2,2 0 0,0 18,4A2,2 0 0,0 16,6V8H18Z",W="M11,4H13V16L18.5,10.5L19.92,11.92L12,19.84L4.08,11.92L5.5,10.5L11,16V4Z",U="M13,20H11V8L5.5,13.5L4.08,12.08L12,4.16L19.92,12.08L18.5,13.5L13,8V20Z",K="M19,21H8V7H19M19,5H8A2,2 0 0,0 6,7V21A2,2 0 0,0 8,23H19A2,2 0 0,0 21,21V7A2,2 0 0,0 19,5M16,1H4A2,2 0 0,0 2,3V17H4V3H16V1Z",j="M19,3L13,9L15,11L22,4V3M12,12.5A0.5,0.5 0 0,1 11.5,12A0.5,0.5 0 0,1 12,11.5A0.5,0.5 0 0,1 12.5,12A0.5,0.5 0 0,1 12,12.5M6,20A2,2 0 0,1 4,18C4,16.89 4.9,16 6,16A2,2 0 0,1 8,18C8,19.11 7.1,20 6,20M6,8A2,2 0 0,1 4,6C4,4.89 4.9,4 6,4A2,2 0 0,1 8,6C8,7.11 7.1,8 6,8M9.64,7.64C9.87,7.14 10,6.59 10,6A4,4 0 0,0 6,2A4,4 0 0,0 2,6A4,4 0 0,0 6,10C6.59,10 7.14,9.87 7.64,9.64L10,12L7.64,14.36C7.14,14.13 6.59,14 6,14A4,4 0 0,0 2,18A4,4 0 0,0 6,22A4,4 0 0,0 10,18C10,17.41 9.87,16.86 9.64,16.36L12,14L19,21H22V20L9.64,7.64Z",Y="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",J="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z",G="M8,5.14V19.14L19,12.14L8,5.14Z",X="M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M10,16.5L16,12L10,7.5V16.5Z",Q="M3 6V8H14V6H3M3 10V12H14V10H3M20 10.1C19.9 10.1 19.7 10.2 19.6 10.3L18.6 11.3L20.7 13.4L21.7 12.4C21.9 12.2 21.9 11.8 21.7 11.6L20.4 10.3C20.3 10.2 20.2 10.1 20 10.1M18.1 11.9L12 17.9V20H14.1L20.2 13.9L18.1 11.9M3 14V16H10V14H3Z",tt="M16,8H14V11H11V13H14V16H16V13H19V11H16M2,12C2,9.21 3.64,6.8 6,5.68V3.5C2.5,4.76 0,8.09 0,12C0,15.91 2.5,19.24 6,20.5V18.32C3.64,17.2 2,14.79 2,12M15,3C10.04,3 6,7.04 6,12C6,16.96 10.04,21 15,21C19.96,21 24,16.96 24,12C24,7.04 19.96,3 15,3M15,19C11.14,19 8,15.86 8,12C8,8.14 11.14,5 15,5C18.86,5 22,8.14 22,12C22,15.86 18.86,19 15,19Z",et="M18,17H10.5L12.5,15H18M6,17V14.5L13.88,6.65C14.07,6.45 14.39,6.45 14.59,6.65L16.35,8.41C16.55,8.61 16.55,8.92 16.35,9.12L8.47,17M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3Z",it="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4M9,9V15H15V9",ot=(0,c.A)((t=>{if(t)return"action"in t?(0,C.pq)(t):M.I8.some((e=>e in t))?"condition":Object.keys($.O$).find((e=>e in t))})),at=(t,e)=>{e.stopPropagation();const i=e.target?.name;if(!i)return;const o=e.detail?.value||e.target.value;if((t.action[i]||"")===o)return;let a;o?a={...t.action,[i]:o}:(a={...t.action},delete a[i]),(0,u.r)(t,"value-changed",{value:a})};class st extends d.WF{get selected(){return this._selected}firstUpdated(t){super.firstUpdated(t),this.root&&(this._collapsed=!1)}willUpdate(t){if(t.has("yamlMode")&&(this._warnings=void 0),!t.has("action"))return;const e=ot(this.action);this._uiModeAvailable=void 0!==e&&!$.ix.has(e),this._uiModeAvailable||this._yamlMode||(this._yamlMode=!0)}_renderOverflowLabel(t,e){return d.qy`
      <div class="overflow-label">
        ${t}
        ${this.optionsInSidebar&&!this.narrow?e||d.qy`<span
              class="shortcut-placeholder ${S.c?"mac":""}"
            ></span>`:d.s6}
      </div>
    `}_renderRow(){const t=ot(this.action);return d.qy`
      ${"service"===t&&"action"in this.action&&this.action.action?d.qy`
            <ha-service-icon
              slot="leading-icon"
              class="action-icon"
              .hass=${this.hass}
              .service=${this.action.action}
            ></ha-service-icon>
          `:d.qy`
            <ha-svg-icon
              slot="leading-icon"
              class="action-icon"
              .path=${$.O$[t]}
            ></ha-svg-icon>
          `}
      <h3 slot="header">
        ${(0,v.Z)((0,V.u)(this.hass,this._entityReg,this._labelReg,this._floorReg,this.action))}
      </h3>

      <slot name="icons" slot="icons"></slot>

      ${"condition"!==t&&!0===this.action.continue_on_error?d.qy`<ha-svg-icon
              id="svg-icon"
              slot="icons"
              .path=${N}
            ></ha-svg-icon>
            <ha-tooltip for="svg-icon">
              ${this.hass.localize("ui.panel.config.automation.editor.actions.continue_on_error")}
            </ha-tooltip>`:d.s6}

      <ha-md-button-menu
        quick
        slot="icons"
        @click=${_.C}
        @keydown=${m.d}
        @closed=${m.d}
        positioning="fixed"
        anchor-corner="end-end"
        menu-corner="start-end"
      >
        <ha-icon-button
          slot="trigger"
          .label=${this.hass.localize("ui.common.menu")}
          .path=${J}
        ></ha-icon-button>

        <ha-md-menu-item .clickAction=${this._runAction}>
          <ha-svg-icon slot="start" .path=${G}></ha-svg-icon>
          ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.actions.run"))}
        </ha-md-menu-item>
        <ha-md-menu-item
          .clickAction=${this._renameAction}
          .disabled=${this.disabled}
        >
          <ha-svg-icon slot="start" .path=${et}></ha-svg-icon>
          ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.triggers.rename"))}
        </ha-md-menu-item>
        <ha-md-divider role="separator" tabindex="-1"></ha-md-divider>
        <ha-md-menu-item
          .clickAction=${this._duplicateAction}
          .disabled=${this.disabled}
        >
          <ha-svg-icon
            slot="start"
            .path=${tt}
          ></ha-svg-icon>

          ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.actions.duplicate"))}
        </ha-md-menu-item>

        <ha-md-menu-item
          .clickAction=${this._copyAction}
          .disabled=${this.disabled}
        >
          <ha-svg-icon slot="start" .path=${K}></ha-svg-icon>
          ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.triggers.copy"),d.qy`<span class="shortcut">
              <span
                >${S.c?d.qy`<ha-svg-icon
                      slot="start"
                      .path=${T}
                    ></ha-svg-icon>`:this.hass.localize("ui.panel.config.automation.editor.ctrl")}</span
              >
              <span>+</span>
              <span>C</span>
            </span>`)}
        </ha-md-menu-item>

        <ha-md-menu-item
          .clickAction=${this._cutAction}
          .disabled=${this.disabled}
        >
          <ha-svg-icon slot="start" .path=${j}></ha-svg-icon>
          ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.triggers.cut"),d.qy`<span class="shortcut">
              <span
                >${S.c?d.qy`<ha-svg-icon
                      slot="start"
                      .path=${T}
                    ></ha-svg-icon>`:this.hass.localize("ui.panel.config.automation.editor.ctrl")}</span
              >
              <span>+</span>
              <span>X</span>
            </span>`)}
        </ha-md-menu-item>

        ${this.optionsInSidebar?d.s6:d.qy`
              <ha-md-menu-item
                .clickAction=${this._moveUp}
                .disabled=${this.disabled||!!this.first}
              >
                ${this.hass.localize("ui.panel.config.automation.editor.move_up")}
                <ha-svg-icon slot="start" .path=${U}></ha-svg-icon
              ></ha-md-menu-item>
              <ha-md-menu-item
                .clickAction=${this._moveDown}
                .disabled=${this.disabled||!!this.last}
              >
                ${this.hass.localize("ui.panel.config.automation.editor.move_down")}
                <ha-svg-icon slot="start" .path=${W}></ha-svg-icon
              ></ha-md-menu-item>
            `}

        <ha-md-menu-item
          .clickAction=${this._toggleYamlMode}
          .disabled=${!this._uiModeAvailable||!!this._warnings}
        >
          <ha-svg-icon slot="start" .path=${Q}></ha-svg-icon>
          ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.edit_"+(this._yamlMode?"ui":"yaml")))}
        </ha-md-menu-item>

        <ha-md-divider role="separator" tabindex="-1"></ha-md-divider>

        <ha-md-menu-item
          .clickAction=${this._onDisable}
          .disabled=${this.disabled}
        >
          <ha-svg-icon
            slot="start"
            .path=${!1===this.action.enabled?X:it}
          ></ha-svg-icon>

          ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.actions."+(!1===this.action.enabled?"enable":"disable")))}
        </ha-md-menu-item>
        <ha-md-menu-item
          class="warning"
          .clickAction=${this._onDelete}
          .disabled=${this.disabled}
        >
          <ha-svg-icon
            class="warning"
            slot="start"
            .path=${Y}
          ></ha-svg-icon>

          ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.actions.delete"),d.qy`<span class="shortcut">
              <span
                >${S.c?d.qy`<ha-svg-icon
                      slot="start"
                      .path=${T}
                    ></ha-svg-icon>`:this.hass.localize("ui.panel.config.automation.editor.ctrl")}</span
              >
              <span>+</span>
              <span
                >${this.hass.localize("ui.panel.config.automation.editor.del")}</span
              >
            </span>`)}
        </ha-md-menu-item>
      </ha-md-button-menu>

      ${this.optionsInSidebar?d.s6:d.qy`${this._warnings?d.qy`<ha-automation-editor-warning
                  .localize=${this.hass.localize}
                  .warnings=${this._warnings}
                >
                </ha-automation-editor-warning>`:d.s6}
            <ha-automation-action-editor
              .hass=${this.hass}
              .action=${this.action}
              .disabled=${this.disabled}
              .yamlMode=${this._yamlMode}
              .narrow=${this.narrow}
              .uiSupported=${this._uiSupported(t)}
              @ui-mode-not-available=${this._handleUiModeNotAvailable}
            ></ha-automation-action-editor>`}
    `}render(){if(!this.action)return d.s6;const t=ot(this.action),e="repeat"===t?`repeat_${(0,B.m)(this.action.repeat)}`:t;return d.qy`
      <ha-card outlined>
        ${!1===this.action.enabled?d.qy`
              <div class="disabled-bar">
                ${this.hass.localize("ui.panel.config.automation.editor.actions.disabled")}
              </div>
            `:d.s6}
        ${this.optionsInSidebar?d.qy`<ha-automation-row
              .disabled=${!1===this.action.enabled}
              .leftChevron=${[...$.L_,...$.I8].includes(e)||"condition"===e&&M.I8.includes(this.action.condition)}
              .collapsed=${this._collapsed}
              .selected=${this._selected}
              .highlight=${this.highlight}
              .buildingBlock=${[...$.L_,...$.I8].includes(e)}
              .sortSelected=${this.sortSelected}
              @click=${this._toggleSidebar}
              @toggle-collapsed=${this._toggleCollapse}
              >${this._renderRow()}</ha-automation-row
            >`:d.qy`
              <ha-expansion-panel left-chevron>
                ${this._renderRow()}
              </ha-expansion-panel>
            `}
      </ha-card>

      ${this.optionsInSidebar&&([...$.L_,...$.I8].includes(e)||"condition"===e&&M.I8.includes(this.action.condition))?d.qy`<ha-automation-action-editor
            class=${this._collapsed?"hidden":""}
            .hass=${this.hass}
            .action=${this.action}
            .narrow=${this.narrow}
            .disabled=${this.disabled}
            .uiSupported=${this._uiSupported(t)}
            indent
            .selected=${this._selected}
            @value-changed=${this._onValueChange}
          ></ha-automation-action-editor>`:d.s6}
    `}_onValueChange(t){this._selected&&this.optionsInSidebar&&this.openSidebar(t.detail.value)}_setClipboard(){this._clipboard={...this._clipboard,action:(0,n.A)(this.action)},(0,b.l)((0,r.Bh)(this.action))}_switchUiMode(){this._yamlMode=!1}_switchYamlMode(){this._yamlMode=!0}_handleUiModeNotAvailable(t){this._warnings=(0,g._)(this.hass,t.detail).warnings,this._yamlMode||(this._yamlMode=!0)}_toggleSidebar(t){t?.stopPropagation(),this._selected?(0,u.r)(this,"request-close-sidebar"):this.openSidebar()}openSidebar(t){const e=t??this.action,i=ot(e);(0,u.r)(this,"open-sidebar",{save:t=>{(0,u.r)(this,"value-changed",{value:t})},close:t=>{this._selected=!1,(0,u.r)(this,"close-sidebar"),t&&this.focus()},rename:()=>{this._renameAction()},toggleYamlMode:()=>{this._toggleYamlMode(),this.openSidebar()},disable:this._onDisable,delete:this._onDelete,copy:this._copyAction,cut:this._cutAction,duplicate:this._duplicateAction,insertAfter:this._insertAfter,run:this._runAction,config:{action:e},uiSupported:!!i&&this._uiSupported(i),yamlMode:this._yamlMode}),this._selected=!0,this._collapsed=!1,this.narrow&&window.setTimeout((()=>{this.scrollIntoView({block:"start",behavior:"smooth"})}),180)}expand(){this.optionsInSidebar?this._collapsed=!1:this.updateComplete.then((()=>{this.shadowRoot.querySelector("ha-expansion-panel").expanded=!0}))}collapse(){this.optionsInSidebar?this._collapsed=!0:this.updateComplete.then((()=>{this.shadowRoot.querySelector("ha-expansion-panel").expanded=!1}))}expandAll(){this.expand(),this._actionEditor?.expandAll()}collapseAll(){this.collapse(),this._actionEditor?.collapseAll()}_toggleCollapse(){this._collapsed=!this._collapsed}focus(){this._automationRowElement?.focus()}constructor(...t){super(...t),this.narrow=!1,this.disabled=!1,this.root=!1,this.optionsInSidebar=!1,this.sortSelected=!1,this._uiModeAvailable=!0,this._yamlMode=!1,this._selected=!1,this._collapsed=!0,this._onDisable=()=>{const t=!(this.action.enabled??1),e={...this.action,enabled:t};(0,u.r)(this,"value-changed",{value:e}),this._selected&&this.optionsInSidebar&&this.openSidebar(e),this._yamlMode&&!this.optionsInSidebar&&this._actionEditor?.yamlEditor?.setValue(e)},this._runAction=async()=>{requestAnimationFrame((()=>{this.scrollIntoViewIfNeeded?this.scrollIntoViewIfNeeded():this.scrollIntoView()}));const t=await(0,w.$)(this.hass,{actions:this.action});if(t.actions.valid){try{await(0,x.d)(this.hass,this.action)}catch(e){return void(0,H.K$)(this,{title:this.hass.localize("ui.panel.config.automation.editor.actions.run_action_error"),text:e.message||e})}(0,L.P)(this,{message:this.hass.localize("ui.panel.config.automation.editor.actions.run_action_success")})}else(0,H.K$)(this,{title:this.hass.localize("ui.panel.config.automation.editor.actions.invalid_action"),text:t.actions.error})},this._onDelete=()=>{(0,H.dk)(this,{title:this.hass.localize("ui.panel.config.automation.editor.actions.delete_confirm_title"),text:this.hass.localize("ui.panel.config.automation.editor.actions.delete_confirm_text"),dismissText:this.hass.localize("ui.common.cancel"),confirmText:this.hass.localize("ui.common.delete"),destructive:!0,confirm:()=>{(0,u.r)(this,"value-changed",{value:null}),this._selected&&(0,u.r)(this,"close-sidebar")}})},this._renameAction=async()=>{const t=await(0,H.an)(this,{title:this.hass.localize("ui.panel.config.automation.editor.actions.change_alias"),inputLabel:this.hass.localize("ui.panel.config.automation.editor.actions.alias"),inputType:"string",placeholder:(0,v.Z)((0,V.u)(this.hass,this._entityReg,this._labelReg,this._floorReg,this.action,void 0,!0)),defaultValue:this.action.alias,confirmText:this.hass.localize("ui.common.submit")});if(null!==t){const e={...this.action};""===t?delete e.alias:e.alias=t,(0,u.r)(this,"value-changed",{value:e}),this._selected&&this.optionsInSidebar?this.openSidebar(e):this._yamlMode&&this._actionEditor?.yamlEditor?.setValue(e)}},this._duplicateAction=()=>{(0,u.r)(this,"duplicate")},this._insertAfter=t=>!(0,h.e)(t).some((t=>!(0,C.ve)(t)))&&((0,u.r)(this,"insert-after",{value:t}),!0),this._copyAction=()=>{this._setClipboard(),(0,L.P)(this,{message:this.hass.localize("ui.panel.config.automation.editor.actions.copied_to_clipboard"),duration:2e3})},this._cutAction=()=>{this._setClipboard(),(0,u.r)(this,"value-changed",{value:null}),this._selected&&(0,u.r)(this,"close-sidebar"),(0,L.P)(this,{message:this.hass.localize("ui.panel.config.automation.editor.actions.cut_to_clipboard"),duration:2e3})},this._moveUp=()=>{(0,u.r)(this,"move-up")},this._moveDown=()=>{(0,u.r)(this,"move-down")},this._toggleYamlMode=t=>{this._yamlMode?this._switchUiMode():this._switchYamlMode(),this.optionsInSidebar?t&&this.openSidebar():this.expand()},this._uiSupported=(0,c.A)((t=>void 0!==customElements.get(`ha-automation-action-${t}`)))}}st.styles=[Z.bH,Z.Lt],(0,a.__decorate)([(0,l.MZ)({attribute:!1})],st.prototype,"hass",void 0),(0,a.__decorate)([(0,l.MZ)({attribute:!1})],st.prototype,"action",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],st.prototype,"narrow",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],st.prototype,"disabled",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],st.prototype,"root",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],st.prototype,"first",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],st.prototype,"last",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],st.prototype,"highlight",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean,attribute:"sidebar"})],st.prototype,"optionsInSidebar",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean,attribute:"sort-selected"})],st.prototype,"sortSelected",void 0),(0,a.__decorate)([(0,p.I)({key:"automationClipboard",state:!1,subscribe:!0,storage:"sessionStorage"})],st.prototype,"_clipboard",void 0),(0,a.__decorate)([(0,l.wk)(),(0,s.Fg)({context:A.ih,subscribe:!0})],st.prototype,"_entityReg",void 0),(0,a.__decorate)([(0,l.wk)(),(0,s.Fg)({context:A.HD,subscribe:!0})],st.prototype,"_labelReg",void 0),(0,a.__decorate)([(0,l.wk)(),(0,s.Fg)({context:A.rf,subscribe:!0})],st.prototype,"_floorReg",void 0),(0,a.__decorate)([(0,l.wk)()],st.prototype,"_uiModeAvailable",void 0),(0,a.__decorate)([(0,l.wk)()],st.prototype,"_yamlMode",void 0),(0,a.__decorate)([(0,l.wk)()],st.prototype,"_selected",void 0),(0,a.__decorate)([(0,l.wk)()],st.prototype,"_collapsed",void 0),(0,a.__decorate)([(0,l.wk)()],st.prototype,"_warnings",void 0),(0,a.__decorate)([(0,l.P)("ha-automation-action-editor")],st.prototype,"_actionEditor",void 0),(0,a.__decorate)([(0,l.P)("ha-automation-row")],st.prototype,"_automationRowElement",void 0),st=(0,a.__decorate)([(0,l.EM)("ha-automation-action-row")],st),o()}catch(N){o(N)}}))},32020:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(97481),s=i(84922),n=i(11991),r=i(33055),d=i(83490),l=i(73120),c=i(20674),h=i(93360),p=i(76943),u=(i(8115),i(95635),i(95475)),_=i(20850),m=i(68975),v=i(18373),g=i(26846),b=t([p,v]);[p,v]=b.then?(await b)():b;const y="M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z",f="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";class $ extends s.WF{render(){return s.qy`
      <ha-sortable
        handle-selector=".handle"
        draggable-selector="ha-automation-action-row"
        .disabled=${this.disabled}
        group="actions"
        invert-swap
        @item-moved=${this._actionMoved}
        @item-added=${this._actionAdded}
        @item-removed=${this._actionRemoved}
      >
        <div class="rows ${this.optionsInSidebar?"":"no-sidebar"}">
          ${(0,r.u)(this.actions,(t=>this._getKey(t)),((t,e)=>s.qy`
              <ha-automation-action-row
                .root=${this.root}
                .sortableData=${t}
                .index=${e}
                .first=${0===e}
                .last=${e===this.actions.length-1}
                .action=${t}
                .narrow=${this.narrow}
                .disabled=${this.disabled}
                @duplicate=${this._duplicateAction}
                @insert-after=${this._insertAfter}
                @move-down=${this._moveDown}
                @move-up=${this._moveUp}
                @value-changed=${this._actionChanged}
                .hass=${this.hass}
                .highlight=${this.highlightedActions?.includes(t)}
                .optionsInSidebar=${this.optionsInSidebar}
                .sortSelected=${this._rowSortSelected===e}
                @stop-sort-selection=${this._stopSortSelection}
              >
                ${this.disabled?s.s6:s.qy`
                      <div
                        tabindex="0"
                        class="handle ${this._rowSortSelected===e?"active":""}"
                        slot="icons"
                        @keydown=${this._handleDragKeydown}
                        @click=${c.d}
                        .index=${e}
                      >
                        <ha-svg-icon .path=${y}></ha-svg-icon>
                      </div>
                    `}
              </ha-automation-action-row>
            `))}
          <div class="buttons">
            <ha-button
              .disabled=${this.disabled}
              @click=${this._addActionDialog}
              .appearance=${this.root?"accent":"filled"}
              .size=${this.root?"medium":"small"}
            >
              <ha-svg-icon .path=${f} slot="start"></ha-svg-icon>
              ${this.hass.localize("ui.panel.config.automation.editor.actions.add")}
            </ha-button>
            <ha-button
              .disabled=${this.disabled}
              @click=${this._addActionBuildingBlockDialog}
              appearance="plain"
              .size=${this.root?"medium":"small"}
            >
              <ha-svg-icon .path=${f} slot="start"></ha-svg-icon>
              ${this.hass.localize("ui.panel.config.automation.editor.actions.add_building_block")}
            </ha-button>
          </div>
        </div>
      </ha-sortable>
    `}updated(t){if(super.updated(t),t.has("actions")&&(this._focusLastActionOnChange||void 0!==this._focusActionIndexOnChange)){const t=this._focusLastActionOnChange?"new":"moved",e=this.shadowRoot.querySelector("ha-automation-action-row:"+("new"===t?"last-of-type":`nth-of-type(${this._focusActionIndexOnChange+1})`));this._focusLastActionOnChange=!1,this._focusActionIndexOnChange=void 0,e.updateComplete.then((()=>{const i=(0,v.MS)(e.action);!i||!this.optionsInSidebar||u.L_.includes(i)&&"moved"!==t||(e.openSidebar(),this.narrow&&e.scrollIntoView({block:"start",behavior:"smooth"})),"new"===t&&e.expand(),this.optionsInSidebar||e.focus()}))}}expandAll(){this._actionRowElements?.forEach((t=>{t.expandAll()}))}collapseAll(){this._actionRowElements?.forEach((t=>{t.collapseAll()}))}_addActionDialog(){this.narrow&&(0,l.r)(this,"request-close-sidebar"),(0,_.gZ)(this,{type:"action",add:this._addAction,clipboardItem:(0,v.MS)(this._clipboard?.action)})}_addActionBuildingBlockDialog(){(0,_.gZ)(this,{type:"action",add:this._addAction,clipboardItem:(0,v.MS)(this._clipboard?.action),group:"building_blocks"})}_getKey(t){return this._actionKeys.has(t)||this._actionKeys.set(t,Math.random().toString()),this._actionKeys.get(t)}async _moveUp(t){t.stopPropagation();const e=t.target.index;if(!t.target.first){const i=e-1;this._move(e,i),this._rowSortSelected===e&&(this._rowSortSelected=i),t.target.focus()}}async _moveDown(t){t.stopPropagation();const e=t.target.index;if(!t.target.last){const i=e+1;this._move(e,i),this._rowSortSelected===e&&(this._rowSortSelected=i),t.target.focus()}}_move(t,e){const i=this.actions.concat(),o=i.splice(t,1)[0];i.splice(e,0,o),this.actions=i,(0,l.r)(this,"value-changed",{value:i})}_actionMoved(t){t.stopPropagation();const{oldIndex:e,newIndex:i}=t.detail;this._move(e,i)}async _actionAdded(t){t.stopPropagation();const{index:e,data:i}=t.detail,o=t.detail.item.selected;let a=[...this.actions.slice(0,e),i,...this.actions.slice(e)];this.actions=a,o&&(this._focusActionIndexOnChange=1===a.length?0:e),await(0,h.E)(),this.actions!==a&&(a=[...this.actions.slice(0,e),i,...this.actions.slice(e)],o&&(this._focusActionIndexOnChange=1===a.length?0:e)),(0,l.r)(this,"value-changed",{value:a})}async _actionRemoved(t){t.stopPropagation();const{index:e}=t.detail,i=this.actions[e];this.actions=this.actions.filter((t=>t!==i)),await(0,h.E)();const o=this.actions.filter((t=>t!==i));(0,l.r)(this,"value-changed",{value:o})}_actionChanged(t){t.stopPropagation();const e=[...this.actions],i=t.detail.value,o=t.target.index;if(null===i)e.splice(o,1);else{const t=this._getKey(e[o]);this._actionKeys.set(i,t),e[o]=i}(0,l.r)(this,"value-changed",{value:e})}_duplicateAction(t){t.stopPropagation();const e=t.target.index;(0,l.r)(this,"value-changed",{value:this.actions.toSpliced(e+1,0,(0,a.A)(this.actions[e]))})}_insertAfter(t){t.stopPropagation();const e=t.target.index,i=(0,g.e)(t.detail.value);this.highlightedActions=i,(0,l.r)(this,"value-changed",{value:this.actions.toSpliced(e+1,0,...i)})}_handleDragKeydown(t){"Enter"!==t.key&&" "!==t.key||(t.stopPropagation(),this._rowSortSelected=void 0===this._rowSortSelected?t.target.index:void 0)}_stopSortSelection(){this._rowSortSelected=void 0}constructor(...t){super(...t),this.narrow=!1,this.disabled=!1,this.root=!1,this.optionsInSidebar=!1,this._focusLastActionOnChange=!1,this._actionKeys=new WeakMap,this._addAction=t=>{let e;if(t===_.uV)e=this.actions.concat((0,a.A)(this._clipboard.action));else if(t in _.EN)e=this.actions.concat(_.EN[t]);else if((0,u.kd)(t))e=this.actions.concat({action:(0,u.cQ)(t),metadata:{}});else{const i=customElements.get(`ha-automation-action-${t}`);e=this.actions.concat(i?{...i.defaultConfig}:{[t]:{}})}this._focusLastActionOnChange=!0,(0,l.r)(this,"value-changed",{value:e})}}}$.styles=m.Ju,(0,o.__decorate)([(0,n.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],$.prototype,"narrow",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],$.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],$.prototype,"root",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],$.prototype,"actions",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],$.prototype,"highlightedActions",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"sidebar"})],$.prototype,"optionsInSidebar",void 0),(0,o.__decorate)([(0,n.wk)()],$.prototype,"_rowSortSelected",void 0),(0,o.__decorate)([(0,n.wk)(),(0,d.I)({key:"automationClipboard",state:!0,subscribe:!0,storage:"sessionStorage"})],$.prototype,"_clipboard",void 0),(0,o.__decorate)([(0,n.YG)("ha-automation-action-row")],$.prototype,"_actionRowElements",void 0),$=(0,o.__decorate)([(0,n.EM)("ha-automation-action")],$),e()}catch(y){e(y)}}))},44158:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(84922),s=i(11991),n=i(26846),r=i(73120),d=i(83566),l=i(65814),c=i(10611),h=i(68975),p=i(32020),u=t([l,c,p]);[l,c,p]=u.then?(await u)():u;class _ extends a.WF{static get defaultConfig(){return{choose:[{conditions:[],sequence:[]}]}}render(){const t=this.action,e=t.choose?(0,n.e)(t.choose):[];return a.qy`
      <ha-automation-option
        .options=${e}
        .disabled=${this.disabled}
        @value-changed=${this._optionsChanged}
        .hass=${this.hass}
        .narrow=${this.narrow}
        .optionsInSidebar=${this.indent}
        .showDefaultActions=${this._showDefault||!!t.default}
        @show-default-actions=${this._addDefault}
      ></ha-automation-option>

      ${this._showDefault||t.default?a.qy`
            <ha-automation-option-row
              .defaultActions=${(0,n.e)(t.default)||[]}
              .narrow=${this.narrow}
              .disabled=${this.disabled}
              .hass=${this.hass}
              .optionsInSidebar=${this.indent}
              @value-changed=${this._defaultChanged}
            ></ha-automation-option-row>
          `:a.s6}
    `}async _addDefault(){this._showDefault=!0,await(this._defaultOptionRowElement?.updateComplete),this._defaultOptionRowElement?.expand()}_optionsChanged(t){t.stopPropagation();const e=t.detail.value;(0,r.r)(this,"value-changed",{value:{...this.action,choose:e}})}_defaultChanged(t){t.stopPropagation(),this._showDefault=!0;const e=t.detail.value,i={...this.action,default:e};0===e.length&&delete i.default,(0,r.r)(this,"value-changed",{value:i})}expandAll(){this._optionElement?.expandAll(),this._defaultOptionRowElement?.expandAll()}collapseAll(){this._optionElement?.collapseAll(),this._defaultOptionRowElement?.collapseAll()}static get styles(){return[d.RF,h.aM,a.AH`
        ha-automation-option-row {
          display: block;
          margin-top: 24px;
        }
        h3 {
          font-size: inherit;
          font-weight: inherit;
        }
      `]}constructor(...t){super(...t),this.disabled=!1,this.narrow=!1,this.indent=!1,this._showDefault=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],_.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],_.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],_.prototype,"indent",void 0),(0,o.__decorate)([(0,s.wk)()],_.prototype,"_showDefault",void 0),(0,o.__decorate)([(0,s.P)("ha-automation-option")],_.prototype,"_optionElement",void 0),(0,o.__decorate)([(0,s.P)("ha-automation-option-row")],_.prototype,"_defaultOptionRowElement",void 0),_=(0,o.__decorate)([(0,s.EM)("ha-automation-action-choose")],_),e()}catch(_){e(_)}}))},68130:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(84922),s=i(11991),n=i(65940),r=i(73120),d=i(90963),l=i(20674),c=(i(25223),i(37207),i(32588)),h=i(19698),p=i(74500),u=(i(93273),i(46820)),_=i(65292),m=i(33e3),v=(i(63848),i(52843),i(79455)),g=(i(53028),i(59745),i(36771)),b=t([h,p,u,_,m,v,g]);[h,p,u,_,m,v,g]=b.then?(await b)():b;class y extends a.WF{static get defaultConfig(){return{condition:"state"}}render(){const t=c.I8.includes(this.action.condition);return a.qy`
      ${this.inSidebar||!this.inSidebar&&!this.indent?a.qy`
            <ha-select
              fixedMenuPosition
              .label=${this.hass.localize("ui.panel.config.automation.editor.conditions.type_select")}
              .disabled=${this.disabled}
              .value=${this.action.condition}
              naturalMenuWidth
              @selected=${this._typeChanged}
              @closed=${l.d}
            >
              ${this._processedTypes(this.hass.localize).map((([t,e,i])=>a.qy`
                  <ha-list-item .value=${t} graphic="icon">
                    ${e}<ha-svg-icon
                      slot="graphic"
                      .path=${i}
                    ></ha-svg-icon
                  ></ha-list-item>
                `))}
            </ha-select>
          `:a.s6}
      ${this.indent&&t||this.inSidebar&&!t||!this.indent&&!this.inSidebar?a.qy`
            <ha-automation-condition-editor
              .condition=${this.action}
              .disabled=${this.disabled}
              .hass=${this.hass}
              @value-changed=${this._conditionChanged}
              .narrow=${this.narrow}
              .uiSupported=${this._uiSupported(this.action.condition)}
              .indent=${this.indent}
              action
            ></ha-automation-condition-editor>
          `:a.s6}
    `}_conditionChanged(t){t.stopPropagation(),(0,r.r)(this,"value-changed",{value:t.detail.value})}_typeChanged(t){const e=t.target.value;if(!e)return;const i=customElements.get(`ha-automation-condition-${e}`);e!==this.action.condition&&(0,r.r)(this,"value-changed",{value:{...i.defaultConfig}})}expandAll(){this._conditionEditor?.expandAll()}collapseAll(){this._conditionEditor?.collapseAll()}constructor(...t){super(...t),this.disabled=!1,this.narrow=!1,this.inSidebar=!1,this.indent=!1,this._processedTypes=(0,n.A)((t=>Object.entries(c.Dk).map((([e,i])=>[e,t(`ui.panel.config.automation.editor.conditions.type.${e}.label`),i])).sort(((t,e)=>(0,d.xL)(t[1],e[1],this.hass.locale.language))))),this._uiSupported=(0,n.A)((t=>void 0!==customElements.get(`ha-automation-condition-${t}`)))}}y.styles=a.AH`
    ha-select {
      margin-bottom: 24px;
    }
  `,(0,o.__decorate)([(0,s.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],y.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],y.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"sidebar"})],y.prototype,"inSidebar",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"indent"})],y.prototype,"indent",void 0),(0,o.__decorate)([(0,s.P)("ha-automation-condition-editor")],y.prototype,"_conditionEditor",void 0),y=(0,o.__decorate)([(0,s.EM)("ha-automation-action-condition")],y),e()}catch(y){e(y)}}))},12696:function(t,e,i){var o=i(69868),a=i(84922),s=i(11991),n=i(73120),r=i(71767),d=(i(76450),i(35384));class l extends a.WF{static get defaultConfig(){return{delay:""}}willUpdate(t){t.has("action")&&(this.action&&(0,r.r)(this.action)?(0,n.r)(this,"ui-mode-not-available",Error(this.hass.localize("ui.errors.config.no_template_editor_support"))):this._timeData=(0,d.z)(this.action.delay))}render(){return a.qy`<ha-duration-input
      .label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.delay.delay")}
      .disabled=${this.disabled}
      .data=${this._timeData}
      enable-millisecond
      required
      @value-changed=${this._valueChanged}
    ></ha-duration-input>`}_valueChanged(t){t.stopPropagation();const e=t.detail.value;e&&(0,n.r)(this,"value-changed",{value:{...this.action,delay:e}})}constructor(...t){super(...t),this.disabled=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],l.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"action",void 0),(0,o.__decorate)([(0,s.wk)()],l.prototype,"_timeData",void 0),l=(0,o.__decorate)([(0,s.EM)("ha-automation-action-delay")],l)},72011:function(t,e,i){var o=i(69868),a=i(97809),s=i(84922),n=i(11991),r=i(65940),d=i(73120),l=i(7657),c=i(4822);class h extends c.V{get NO_AUTOMATION_TEXT(){return this.hass.localize("ui.panel.config.devices.automation.actions.no_actions")}get UNKNOWN_AUTOMATION_TEXT(){return this.hass.localize("ui.panel.config.devices.automation.actions.unknown_action")}constructor(){super(l.PV,l.am,(t=>({device_id:t||"",domain:"",entity_id:""})))}}h=(0,o.__decorate)([(0,n.EM)("ha-device-action-picker")],h);i(95710),i(75518);var p=i(24986);class u extends s.WF{static get defaultConfig(){return{device_id:"",domain:"",entity_id:""}}shouldUpdate(t){return!t.has("action")||(!this.action.device_id||this.action.device_id in this.hass.devices||((0,d.r)(this,"ui-mode-not-available",Error(this.hass.localize("ui.panel.config.automation.editor.edit_unknown_device"))),!1))}render(){const t=this._deviceId||this.action.device_id;return s.qy`
      <ha-device-picker
        .value=${t}
        .disabled=${this.disabled}
        @value-changed=${this._devicePicked}
        .hass=${this.hass}
        label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.device_id.label")}
      ></ha-device-picker>
      <ha-device-action-picker
        .value=${this.action}
        .deviceId=${t}
        .disabled=${this.disabled}
        @value-changed=${this._deviceActionPicked}
        .hass=${this.hass}
        label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.device_id.action")}
      ></ha-device-action-picker>
      ${this._capabilities?.extra_fields?.length?s.qy`
            <ha-form
              .hass=${this.hass}
              .data=${this._extraFieldsData(this.action,this._capabilities)}
              .schema=${this._capabilities.extra_fields}
              .disabled=${this.disabled}
              .computeLabel=${(0,l.T_)(this.hass,this.action)}
              .computeHelper=${(0,l.TH)(this.hass,this.action)}
              @value-changed=${this._extraFieldsChanged}
            ></ha-form>
          `:""}
    `}firstUpdated(){this.hass.loadBackendTranslation("device_automation"),this._capabilities||this._getCapabilities(),this.action&&(this._origAction=this.action)}updated(t){const e=t.get("action");e&&!(0,l.Po)(this._entityReg,e,this.action)&&(this._deviceId=void 0,this._getCapabilities())}async _getCapabilities(){this._capabilities=this.action.domain?await(0,l.jR)(this.hass,this.action):void 0}_devicePicked(t){t.stopPropagation(),this._deviceId=t.target.value,void 0===this._deviceId&&(0,d.r)(this,"value-changed",{value:u.defaultConfig})}_deviceActionPicked(t){t.stopPropagation();let e=t.detail.value;this._origAction&&(0,l.Po)(this._entityReg,this._origAction,e)&&(e=this._origAction),(0,d.r)(this,"value-changed",{value:e})}_extraFieldsChanged(t){t.stopPropagation(),(0,d.r)(this,"value-changed",{value:{...this.action,...t.detail.value}})}constructor(...t){super(...t),this.disabled=!1,this._extraFieldsData=(0,r.A)(((t,e)=>{const i={};return e.extra_fields.forEach((e=>{void 0!==t[e.name]&&(i[e.name]=t[e.name])})),i}))}}u.styles=s.AH`
    ha-device-picker {
      display: block;
      margin-bottom: 24px;
    }

    ha-device-action-picker {
      display: block;
    }

    ha-form {
      display: block;
      margin-top: 24px;
    }
  `,(0,o.__decorate)([(0,n.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({type:Object})],u.prototype,"action",void 0),(0,o.__decorate)([(0,n.wk)()],u.prototype,"_deviceId",void 0),(0,o.__decorate)([(0,n.wk)()],u.prototype,"_capabilities",void 0),(0,o.__decorate)([(0,n.wk)(),(0,a.Fg)({context:p.ih,subscribe:!0})],u.prototype,"_entityReg",void 0),u=(0,o.__decorate)([(0,n.EM)("ha-automation-action-device_id")],u)},94819:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(84922),s=i(11991),n=i(73120),r=i(57447),d=i(90683),l=(i(11934),i(79080)),c=i(18373),h=t([r,d,l,c]);[r,d,l,c]=h.then?(await h)():h;class p extends a.WF{static get defaultConfig(){return{event:"",event_data:{}}}updated(t){t.has("action")&&(this._actionData&&this._actionData!==this.action.event_data&&this._yamlEditor&&this._yamlEditor.setValue(this.action.event_data),this._actionData=this.action.event_data)}render(){const{event:t,event_data:e}=this.action;return a.qy`
      <ha-textfield
        .label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.event.event")}
        .value=${t}
        .disabled=${this.disabled}
        @change=${this._eventChanged}
      ></ha-textfield>
      <ha-yaml-editor
        .hass=${this.hass}
        .label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.event.event_data")}
        .name=${"event_data"}
        .readOnly=${this.disabled}
        .defaultValue=${e}
        @value-changed=${this._dataChanged}
      ></ha-yaml-editor>
    `}_dataChanged(t){t.stopPropagation(),t.detail.isValid&&(this._actionData=t.detail.value,(0,c.Pb)(this,t))}_eventChanged(t){t.stopPropagation(),(0,n.r)(this,"value-changed",{value:{...this.action,event:t.target.value}})}constructor(...t){super(...t),this.disabled=!1}}p.styles=a.AH`
    ha-textfield {
      display: block;
    }
  `,(0,o.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"action",void 0),(0,o.__decorate)([(0,s.P)("ha-yaml-editor",!0)],p.prototype,"_yamlEditor",void 0),p=(0,o.__decorate)([(0,s.EM)("ha-automation-action-event")],p),e()}catch(p){e(p)}}))},25056:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(84922),s=i(11991),n=i(73120),r=(i(11934),i(83566)),d=i(32020),l=t([d]);d=(l.then?(await l)():l)[0];class c extends a.WF{static get defaultConfig(){return{if:[],then:[]}}render(){const t=this.action;return a.qy`
      <h4>
        ${this.hass.localize("ui.panel.config.automation.editor.actions.type.if.if")}:
      </h4>
      <ha-automation-condition
        .conditions=${t.if??[]}
        .disabled=${this.disabled}
        @value-changed=${this._ifChanged}
        .hass=${this.hass}
        .narrow=${this.narrow}
        .optionsInSidebar=${this.indent}
      ></ha-automation-condition>

      <h4>
        ${this.hass.localize("ui.panel.config.automation.editor.actions.type.if.then")}:
      </h4>
      <ha-automation-action
        .actions=${t.then??[]}
        .disabled=${this.disabled}
        @value-changed=${this._thenChanged}
        .hass=${this.hass}
        .narrow=${this.narrow}
        .optionsInSidebar=${this.indent}
      ></ha-automation-action>
      <h4>
        ${this.hass.localize("ui.panel.config.automation.editor.actions.type.if.else")}:
      </h4>
      <ha-automation-action
        .actions=${t.else||[]}
        .disabled=${this.disabled}
        @value-changed=${this._elseChanged}
        .hass=${this.hass}
        .narrow=${this.narrow}
        .optionsInSidebar=${this.indent}
      ></ha-automation-action>
    `}_ifChanged(t){t.stopPropagation();const e=t.detail.value;(0,n.r)(this,"value-changed",{value:{...this.action,if:e}})}_thenChanged(t){t.stopPropagation();const e=t.detail.value;(0,n.r)(this,"value-changed",{value:{...this.action,then:e}})}_elseChanged(t){t.stopPropagation();const e=t.detail.value,i={...this.action,else:e};0===e.length&&delete i.else,(0,n.r)(this,"value-changed",{value:i})}expandAll(){this._conditionElement?.expandAll(),this._actionElements?.forEach((t=>t.expandAll?.()))}collapseAll(){this._conditionElement?.collapseAll(),this._actionElements?.forEach((t=>t.collapseAll?.()))}static get styles(){return[r.RF,a.AH`
        h4 {
          color: var(--secondary-text-color);
          margin-bottom: 8px;
        }
        h4:first-child {
          margin-top: 0;
        }
      `]}constructor(...t){super(...t),this.disabled=!1,this.narrow=!1,this.indent=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"indent",void 0),(0,o.__decorate)([(0,s.P)("ha-automation-condition")],c.prototype,"_conditionElement",void 0),(0,o.__decorate)([(0,s.YG)("ha-automation-action")],c.prototype,"_actionElements",void 0),c=(0,o.__decorate)([(0,s.EM)("ha-automation-action-if")],c),e()}catch(c){e(c)}}))},41856:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(84922),s=i(11991),n=i(73120),r=(i(11934),i(83566)),d=i(32020),l=t([d]);d=(l.then?(await l)():l)[0];class c extends a.WF{static get defaultConfig(){return{parallel:[]}}render(){const t=this.action;return a.qy`
      <ha-automation-action
        .actions=${t.parallel}
        .narrow=${this.narrow}
        .disabled=${this.disabled}
        @value-changed=${this._actionsChanged}
        .hass=${this.hass}
        .optionsInSidebar=${this.indent}
      ></ha-automation-action>
    `}_actionsChanged(t){t.stopPropagation();const e=t.detail.value;(0,n.r)(this,"value-changed",{value:{...this.action,parallel:e}})}expandAll(){this._actionElement?.expandAll()}collapseAll(){this._actionElement?.collapseAll()}static get styles(){return r.RF}constructor(...t){super(...t),this.disabled=!1,this.narrow=!1,this.indent=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"indent",void 0),(0,o.__decorate)([(0,s.P)("ha-automation-action")],c.prototype,"_actionElement",void 0),c=(0,o.__decorate)([(0,s.EM)("ha-automation-action-parallel")],c),e()}catch(c){e(c)}}))},44392:function(t,e,i){i.a(t,(async function(t,o){try{i.d(e,{m:()=>_});var a=i(69868),s=i(84922),n=i(11991),r=i(65940),d=i(73120),l=(i(11934),i(83566)),c=i(32020),h=i(71767),p=(i(75518),t([c]));c=(p.then?(await p)():p)[0];const u=["count","while","until","for_each"],_=t=>u.find((e=>e in t));class m extends s.WF{static get defaultConfig(){return{repeat:{count:2,sequence:[]}}}render(){const t=this.action.repeat,e=_(t),i=this._schema(e??"count","count"in t&&"string"==typeof t.count&&(0,h.F)(t.count),this.inSidebar,this.indent),o={...t,type:e};return s.qy`<ha-form
      .hass=${this.hass}
      .data=${o}
      .schema=${i}
      .disabled=${this.disabled}
      @value-changed=${this._valueChanged}
      .computeLabel=${this._computeLabelCallback}
      .narrow=${this.narrow}
    ></ha-form>`}_valueChanged(t){t.stopPropagation();const e=t.detail.value,i=e.type;delete e.type;i!==_(this.action.repeat)&&("count"===i&&(e.count=2,delete e.while,delete e.until,delete e.for_each),"while"===i&&(e.while=e.until??[],delete e.count,delete e.until,delete e.for_each),"until"===i&&(e.until=e.while??[],delete e.count,delete e.while,delete e.for_each),"for_each"===i&&(e.for_each={},delete e.count,delete e.while,delete e.until)),(0,d.r)(this,"value-changed",{value:{...this.action,repeat:{...e}}})}static get styles(){return[l.RF,s.AH`
        ha-textfield {
          margin-top: 16px;
        }
      `]}_getSelectorElements(){if(this._formElement){const t=this._formElement.shadowRoot?.querySelectorAll("ha-selector"),e=[];return t?.forEach((t=>{e.push(...Array.from(t.shadowRoot?.querySelectorAll("ha-selector-condition, ha-selector-action")||[]))})),e}return[]}expandAll(){this._getSelectorElements().forEach((t=>{t.expandAll?.()}))}collapseAll(){this._getSelectorElements().forEach((t=>{t.collapseAll?.()}))}constructor(...t){super(...t),this.disabled=!1,this.narrow=!1,this.inSidebar=!1,this.indent=!1,this._schema=(0,r.A)(((t,e,i,o)=>[..."count"!==t||!i&&(i||o)?[]:[{name:"count",required:!0,selector:e?{template:{}}:{number:{mode:"box",min:1}}}],..."until"!==t&&"while"!==t||!o&&(i||o)?[]:[{name:t,selector:{condition:{optionsInSidebar:o}}}],..."for_each"!==t||!i&&(i||o)?[]:[{name:"for_each",required:!0,selector:{object:{}}}],...o||!i&&!o?[{name:"sequence",selector:{action:{optionsInSidebar:o}}}]:[]])),this._computeLabelCallback=t=>{switch(t.name){case"count":return this.hass.localize("ui.panel.config.automation.editor.actions.type.repeat.type.count.label");case"while":return this.hass.localize("ui.panel.config.automation.editor.actions.type.repeat.type.while.conditions")+":";case"until":return this.hass.localize("ui.panel.config.automation.editor.actions.type.repeat.type.until.conditions")+":";case"for_each":return this.hass.localize("ui.panel.config.automation.editor.actions.type.repeat.type.for_each.items")+":";case"sequence":return this.hass.localize("ui.panel.config.automation.editor.actions.type.repeat.sequence")+":"}return""}}}(0,a.__decorate)([(0,n.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],m.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],m.prototype,"narrow",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],m.prototype,"action",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"sidebar"})],m.prototype,"inSidebar",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"indent"})],m.prototype,"indent",void 0),(0,a.__decorate)([(0,n.P)("ha-form")],m.prototype,"_formElement",void 0),m=(0,a.__decorate)([(0,n.EM)("ha-automation-action-repeat")],m),o()}catch(u){o(u)}}))},52118:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(84922),s=i(11991),n=i(73120),r=(i(11934),i(83566)),d=i(32020),l=t([d]);d=(l.then?(await l)():l)[0];class c extends a.WF{static get defaultConfig(){return{sequence:[]}}render(){const{action:t}=this;return a.qy`
      <ha-automation-action
        .actions=${t.sequence}
        .narrow=${this.narrow}
        .disabled=${this.disabled}
        @value-changed=${this._actionsChanged}
        .hass=${this.hass}
        .optionsInSidebar=${this.indent}
      ></ha-automation-action>
    `}_actionsChanged(t){t.stopPropagation();const e=t.detail.value;(0,n.r)(this,"value-changed",{value:{...this.action,sequence:e}})}expandAll(){this._actionElement?.expandAll()}collapseAll(){this._actionElement?.collapseAll()}static get styles(){return r.RF}constructor(...t){super(...t),this.disabled=!1,this.narrow=!1,this.indent=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"indent",void 0),(0,o.__decorate)([(0,s.P)("ha-automation-action")],c.prototype,"_actionElement",void 0),c=(0,o.__decorate)([(0,s.EM)("ha-automation-action-sequence")],c),e()}catch(c){e(c)}}))},96556:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(84922),s=i(11991),n=i(36207),r=i(73120),d=i(71767),l=i(73628),c=i(17866),h=t([l]);l=(h.then?(await h)():h)[0];class p extends a.WF{static get defaultConfig(){return{action:"",data:{}}}willUpdate(t){if(t.has("action")){try{(0,n.vA)(this.action,c.BD)}catch(e){return void(0,r.r)(this,"ui-mode-not-available",e)}this.action&&Object.entries(this.action).some((([t,e])=>!["data","target"].includes(t)&&(0,d.r)(e)))?(0,r.r)(this,"ui-mode-not-available",Error(this.hass.localize("ui.errors.config.no_template_editor_support"))):this.action.entity_id?(this._action={...this.action,data:{...this.action.data,entity_id:this.action.entity_id}},delete this._action.entity_id):this._action=this.action}}render(){if(!this._action)return a.s6;const[t,e]=this._action.action?this._action.action.split(".",2):[void 0,void 0];return a.qy`
      <ha-service-control
        .narrow=${this.narrow}
        .hass=${this.hass}
        .value=${this._action}
        .disabled=${this.disabled}
        .showAdvanced=${this.hass.userData?.showAdvanced}
        .hidePicker=${!!this._action.metadata}
        @value-changed=${this._actionChanged}
      ></ha-service-control>
      ${t&&e&&this.hass.services[t]?.[e]?.response?a.qy`<ha-settings-row .narrow=${this.narrow}>
            ${this.hass.services[t][e].response.optional?a.qy`<ha-checkbox
                  .checked=${this._action.response_variable||this._responseChecked}
                  .disabled=${this.disabled}
                  @change=${this._responseCheckboxChanged}
                  slot="prefix"
                ></ha-checkbox>`:a.qy`<div slot="prefix" class="checkbox-spacer"></div>`}
            <span slot="heading"
              >${this.hass.localize("ui.panel.config.automation.editor.actions.type.service.response_variable")}</span
            >
            <span slot="description">
              ${this.hass.services[t][e].response.optional?this.hass.localize("ui.panel.config.automation.editor.actions.type.service.has_optional_response"):this.hass.localize("ui.panel.config.automation.editor.actions.type.service.has_response")}
            </span>
            <ha-textfield
              .value=${this._action.response_variable||""}
              .required=${!this.hass.services[t][e].response.optional}
              .disabled=${this.disabled||this.hass.services[t][e].response.optional&&!this._action.response_variable&&!this._responseChecked}
              @change=${this._responseVariableChanged}
            ></ha-textfield>
          </ha-settings-row>`:a.s6}
    `}_actionChanged(t){t.detail.value===this._action&&t.stopPropagation();const e={...this.action,...t.detail.value};if("response_variable"in this.action){const[t,i]=this._action.action?this._action.action.split(".",2):[void 0,void 0];t&&i&&this.hass.services[t]?.[i]&&!("response"in this.hass.services[t][i])&&(delete e.response_variable,this._responseChecked=!1)}(0,r.r)(this,"value-changed",{value:e})}_responseVariableChanged(t){const e={...this.action,response_variable:t.target.value};t.target.value||delete e.response_variable,(0,r.r)(this,"value-changed",{value:e})}_responseCheckboxChanged(t){if(this._responseChecked=t.target.checked,!this._responseChecked){const t={...this.action};delete t.response_variable,(0,r.r)(this,"value-changed",{value:t})}}constructor(...t){super(...t),this.disabled=!1,this.narrow=!1,this._responseChecked=!1}}p.styles=a.AH`
    ha-service-control {
      display: block;
      margin: 0 -16px;
    }
    ha-settings-row {
      margin: 0 -16px;
      padding: var(--service-control-padding, 0 16px);
    }
    ha-settings-row {
      --settings-row-content-width: 100%;
      --settings-row-prefix-display: contents;
      border-top: var(
        --service-control-items-border-top,
        1px solid var(--divider-color)
      );
    }
    ha-checkbox {
      margin-left: -16px;
      margin-inline-start: -16px;
      margin-inline-end: initial;
    }
    .checkbox-spacer {
      width: 32px;
    }
  `,(0,o.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.wk)()],p.prototype,"_action",void 0),(0,o.__decorate)([(0,s.wk)()],p.prototype,"_responseChecked",void 0),p=(0,o.__decorate)([(0,s.EM)("ha-automation-action-service")],p),e()}catch(p){e(p)}}))},99235:function(t,e,i){var o=i(69868),a=i(84922),s=i(11991);i(75518);const n=[{name:"set_conversation_response",selector:{template:{}}}];class r extends a.WF{static get defaultConfig(){return{set_conversation_response:""}}render(){return a.qy`
      <ha-form
        .hass=${this.hass}
        .data=${this.action}
        .schema=${n}
        .disabled=${this.disabled}
        .computeLabel=${this._computeLabelCallback}
      ></ha-form>
    `}constructor(...t){super(...t),this.disabled=!1,this._computeLabelCallback=()=>this.hass.localize("ui.panel.config.automation.editor.actions.type.set_conversation_response.label")}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],r.prototype,"disabled",void 0),r=(0,o.__decorate)([(0,s.EM)("ha-automation-action-set_conversation_response")],r)},28975:function(t,e,i){var o=i(69868),a=i(84922),s=i(11991),n=i(73120);i(11934),i(52893),i(43143);class r extends a.WF{static get defaultConfig(){return{stop:""}}render(){const{error:t,stop:e,response_variable:i}=this.action;return a.qy`
      <ha-textfield
        .label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.stop.stop")}
        .value=${e}
        .disabled=${this.disabled}
        @change=${this._stopChanged}
      ></ha-textfield>
      <ha-textfield
        .label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.stop.response_variable")}
        .value=${i||""}
        .disabled=${this.disabled}
        @change=${this._responseChanged}
      ></ha-textfield>
      <ha-formfield
        .disabled=${this.disabled}
        .label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.stop.error")}
      >
        <ha-switch
          .disabled=${this.disabled}
          .checked=${t??!1}
          @change=${this._errorChanged}
        ></ha-switch>
      </ha-formfield>
    `}_stopChanged(t){t.stopPropagation(),(0,n.r)(this,"value-changed",{value:{...this.action,stop:t.target.value}})}_responseChanged(t){t.stopPropagation(),(0,n.r)(this,"value-changed",{value:{...this.action,response_variable:t.target.value}})}_errorChanged(t){t.stopPropagation(),(0,n.r)(this,"value-changed",{value:{...this.action,error:t.target.checked}})}constructor(...t){super(...t),this.disabled=!1}}r.styles=a.AH`
    ha-textfield {
      display: block;
      margin-bottom: 24px;
    }
  `,(0,o.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],r.prototype,"disabled",void 0),r=(0,o.__decorate)([(0,s.EM)("ha-automation-action-stop")],r)},62353:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(84922),s=i(11991),n=i(26846),r=i(35384),d=i(73120),l=(i(76450),i(52893),i(11934),i(21242)),c=i(18373),h=t([l,c]);[l,c]=h.then?(await h)():h;class p extends a.WF{static get defaultConfig(){return{wait_for_trigger:[]}}render(){const t=(0,r.z)(this.action.timeout);return a.qy`
      ${this.inSidebar||!this.inSidebar&&!this.indent?a.qy`
            <ha-duration-input
              .label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.wait_for_trigger.timeout")}
              .data=${t}
              .disabled=${this.disabled}
              enable-millisecond
              @value-changed=${this._timeoutChanged}
            ></ha-duration-input>
            <ha-formfield
              .disabled=${this.disabled}
              .label=${this.hass.localize("ui.panel.config.automation.editor.actions.type.wait_for_trigger.continue_timeout")}
            >
              <ha-switch
                .checked=${this.action.continue_on_timeout??!0}
                .disabled=${this.disabled}
                @change=${this._continueChanged}
              ></ha-switch>
            </ha-formfield>
          `:a.s6}
      ${this.indent||!this.inSidebar&&!this.indent?a.qy`<ha-automation-trigger
            class=${this.inSidebar||this.indent?"":"expansion-panel"}
            .triggers=${(0,n.e)(this.action.wait_for_trigger)}
            .hass=${this.hass}
            .disabled=${this.disabled}
            .name=${"wait_for_trigger"}
            @value-changed=${this._valueChanged}
            .optionsInSidebar=${this.indent}
            .narrow=${this.narrow}
          ></ha-automation-trigger>`:a.s6}
    `}_timeoutChanged(t){t.stopPropagation();const e=t.detail.value;(0,d.r)(this,"value-changed",{value:{...this.action,timeout:e}})}_continueChanged(t){(0,d.r)(this,"value-changed",{value:{...this.action,continue_on_timeout:t.target.checked}})}_valueChanged(t){(0,c.Pb)(this,t)}constructor(...t){super(...t),this.disabled=!1,this.narrow=!1,this.inSidebar=!1,this.indent=!1}}p.styles=a.AH`
    ha-duration-input {
      display: block;
      margin-bottom: 24px;
    }
    ha-automation-trigger.expansion-panel {
      display: block;
      margin-top: 24px;
    }
  `,(0,o.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"sidebar"})],p.prototype,"inSidebar",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"indent"})],p.prototype,"indent",void 0),p=(0,o.__decorate)([(0,s.EM)("ha-automation-action-wait_for_trigger")],p),e()}catch(p){e(p)}}))},55639:function(t,e,i){var o=i(69868),a=i(84922),s=i(11991);i(75518);const n=[{name:"wait_template",selector:{template:{}}},{name:"timeout",required:!1,selector:{text:{}}},{name:"continue_on_timeout",selector:{boolean:{}}}];class r extends a.WF{static get defaultConfig(){return{wait_template:"",continue_on_timeout:!0}}render(){return a.qy`
      <ha-form
        .hass=${this.hass}
        .data=${this.action}
        .schema=${n}
        .disabled=${this.disabled}
        .computeLabel=${this._computeLabelCallback}
      ></ha-form>
    `}constructor(...t){super(...t),this.disabled=!1,this._computeLabelCallback=t=>this.hass.localize(`ui.panel.config.automation.editor.actions.type.wait_template.${"continue_on_timeout"===t.name?"continue_timeout":t.name}`)}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"action",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],r.prototype,"disabled",void 0),r=(0,o.__decorate)([(0,s.EM)("ha-automation-action-wait_template")],r)},10611:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(97809),s=i(84922),n=i(11991),r=i(75907),d=i(26846),l=i(73120),c=i(88727),h=i(20674),p=i(8692),u=(i(29897),i(86853),i(99741),i(93672),i(61647),i(70154),i(95635),i(10101)),_=i(24986),m=i(47420),v=i(52493),g=i(32020),b=i(45290),y=i(68975),f=t([g,b,u]);[g,b,u]=f.then?(await f)():f;const $="M6,2A4,4 0 0,1 10,6V8H14V6A4,4 0 0,1 18,2A4,4 0 0,1 22,6A4,4 0 0,1 18,10H16V14H18A4,4 0 0,1 22,18A4,4 0 0,1 18,22A4,4 0 0,1 14,18V16H10V18A4,4 0 0,1 6,22A4,4 0 0,1 2,18A4,4 0 0,1 6,14H8V10H6A4,4 0 0,1 2,6A4,4 0 0,1 6,2M16,18A2,2 0 0,0 18,20A2,2 0 0,0 20,18A2,2 0 0,0 18,16H16V18M14,10H10V14H14V10M6,16A2,2 0 0,0 4,18A2,2 0 0,0 6,20A2,2 0 0,0 8,18V16H6M8,6A2,2 0 0,0 6,4A2,2 0 0,0 4,6A2,2 0 0,0 6,8H8V6M18,8A2,2 0 0,0 20,6A2,2 0 0,0 18,4A2,2 0 0,0 16,6V8H18Z",M="M11,4H13V16L18.5,10.5L19.92,11.92L12,19.84L4.08,11.92L5.5,10.5L11,16V4Z",w="M13,20H11V8L5.5,13.5L4.08,12.08L12,4.16L19.92,12.08L18.5,13.5L13,8V20Z",A="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",C="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z",V="M16,8H14V11H11V13H14V16H16V13H19V11H16M2,12C2,9.21 3.64,6.8 6,5.68V3.5C2.5,4.76 0,8.09 0,12C0,15.91 2.5,19.24 6,20.5V18.32C3.64,17.2 2,14.79 2,12M15,3C10.04,3 6,7.04 6,12C6,16.96 10.04,21 15,21C19.96,21 24,16.96 24,12C24,7.04 19.96,3 15,3M15,19C11.14,19 8,15.86 8,12C8,8.14 11.14,5 15,5C18.86,5 22,8.14 22,12C22,15.86 18.86,19 15,19Z",x="M18,17H10.5L12.5,15H18M6,17V14.5L13.88,6.65C14.07,6.45 14.39,6.45 14.59,6.65L16.35,8.41C16.55,8.61 16.55,8.92 16.35,9.12L8.47,17M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3Z";class H extends s.WF{get selected(){return this._selected}_expandedChanged(t){"option"===t.currentTarget.id&&(this._expanded=t.detail.expanded)}_getDescription(){const t=(0,d.e)(this.option.conditions);if(!t||0===t.length)return this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.no_conditions");let e="";return"string"==typeof t[0]?e+=t[0]:e+=(0,u.p)(t[0],this.hass,this._entityReg),t.length>1&&(e+=this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.option_description_additional",{numberOfAdditionalConditions:t.length-1})),e}_renderOverflowLabel(t,e){return s.qy`
      <div class="overflow-label">
        ${t}
        ${this.optionsInSidebar&&!this.narrow?e||s.qy`<span
              class="shortcut-placeholder ${v.c?"mac":""}"
            ></span>`:s.s6}
      </div>
    `}_renderRow(){return s.qy`
      <h3 slot="header">
        ${this.option?`${this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.option",{number:this.index+1})}: ${this.option.alias||(this._expanded?"":this._getDescription())}`:this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.default")}
      </h3>

      <slot name="icons" slot="icons"></slot>

      ${this.option?s.qy`
            <ha-md-button-menu
              quick
              slot="icons"
              @click=${c.C}
              @closed=${h.d}
              @keydown=${h.d}
              positioning="fixed"
              anchor-corner="end-end"
              menu-corner="start-end"
            >
              <ha-icon-button
                slot="trigger"
                .label=${this.hass.localize("ui.common.menu")}
                .path=${C}
              ></ha-icon-button>

              <ha-md-menu-item
                @click=${this._renameOption}
                .disabled=${this.disabled}
              >
                <ha-svg-icon slot="start" .path=${x}></ha-svg-icon>
                ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.triggers.rename"))}
              </ha-md-menu-item>

              <ha-md-menu-item
                @click=${this._duplicateOption}
                .disabled=${this.disabled}
              >
                <ha-svg-icon
                  slot="start"
                  .path=${V}
                ></ha-svg-icon>

                ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.actions.duplicate"))}
              </ha-md-menu-item>

              ${this.optionsInSidebar?s.s6:s.qy`
                    <ha-md-menu-item
                      .clickAction=${this._moveUp}
                      .disabled=${this.disabled||!!this.first}
                    >
                      ${this.hass.localize("ui.panel.config.automation.editor.move_up")}
                      <ha-svg-icon
                        slot="start"
                        .path=${w}
                      ></ha-svg-icon
                    ></ha-md-menu-item>
                    <ha-md-menu-item
                      .clickAction=${this._moveDown}
                      .disabled=${this.disabled||!!this.last}
                    >
                      ${this.hass.localize("ui.panel.config.automation.editor.move_down")}
                      <ha-svg-icon
                        slot="start"
                        .path=${M}
                      ></ha-svg-icon
                    ></ha-md-menu-item>
                  `}

              <ha-md-menu-item
                @click=${this._removeOption}
                class="warning"
                .disabled=${this.disabled}
              >
                <ha-svg-icon
                  class="warning"
                  slot="start"
                  .path=${A}
                ></ha-svg-icon>
                ${this._renderOverflowLabel(this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.remove_option"),s.qy`<span class="shortcut">
                    <span
                      >${v.c?s.qy`<ha-svg-icon
                            slot="start"
                            .path=${$}
                          ></ha-svg-icon>`:this.hass.localize("ui.panel.config.automation.editor.ctrl")}</span
                    >
                    <span>+</span>
                    <span
                      >${this.hass.localize("ui.panel.config.automation.editor.del")}</span
                    >
                  </span>`)}
              </ha-md-menu-item>
            </ha-md-button-menu>
          `:s.s6}
      ${this.optionsInSidebar?s.s6:this._renderContent()}
    `}_renderContent(){return s.qy`<div
      class=${(0,r.H)({"card-content":!0,card:!this.optionsInSidebar,indent:this.optionsInSidebar,selected:this._selected,hidden:this.optionsInSidebar&&this._collapsed})}
    >
      ${this.option?s.qy`
            <h4 class="top">
              ${this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.conditions")}:
            </h4>
            <ha-automation-condition
              .conditions=${(0,d.e)(this.option.conditions)}
              .disabled=${this.disabled}
              .hass=${this.hass}
              .narrow=${this.narrow}
              @value-changed=${this._conditionChanged}
              .optionsInSidebar=${this.optionsInSidebar}
            ></ha-automation-condition>
          `:s.s6}
      <h4 class=${this.option?"":"top"}>
        ${this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.sequence")}:
      </h4>
      <ha-automation-action
        .actions=${this.option?(0,d.e)(this.option.sequence)||[]:this.defaultActions&&(0,d.e)(this.defaultActions)||[]}
        .disabled=${this.disabled}
        .hass=${this.hass}
        .narrow=${this.narrow}
        @value-changed=${this._actionChanged}
        .optionsInSidebar=${this.optionsInSidebar}
      ></ha-automation-action>
    </div>`}render(){return this.option||this.defaultActions?s.qy`
      <ha-card outlined class=${this._selected?"selected":""}>
        ${this.optionsInSidebar?s.qy`<ha-automation-row
              left-chevron
              .collapsed=${this._collapsed}
              .selected=${this._selected}
              .sortSelected=${this.sortSelected}
              @click=${this._toggleSidebar}
              @toggle-collapsed=${this._toggleCollapse}
              @delete-row=${this._removeOption}
              >${this._renderRow()}</ha-automation-row
            >`:s.qy`
              <ha-expansion-panel
                left-chevron
                @expanded-changed=${this._expandedChanged}
                id="option"
              >
                ${this._renderRow()}
              </ha-expansion-panel>
            `}
      </ha-card>

      ${this.optionsInSidebar?this._renderContent():s.s6}
    `:s.s6}_moveUp(){(0,l.r)(this,"move-up")}_moveDown(){(0,l.r)(this,"move-down")}_conditionChanged(t){t.stopPropagation();const e=t.detail.value,i={...this.option,conditions:e};(0,l.r)(this,"value-changed",{value:i})}_actionChanged(t){if(this.defaultActions)return;t.stopPropagation();const e=t.detail.value,i={...this.option,sequence:e};(0,l.r)(this,"value-changed",{value:i})}_toggleSidebar(t){t?.stopPropagation(),this._selected?(0,l.r)(this,"request-close-sidebar"):this.openSidebar()}openSidebar(){(0,l.r)(this,"open-sidebar",{close:t=>{this._selected=!1,(0,l.r)(this,"close-sidebar"),t&&this.focus()},rename:()=>{this._renameOption()},delete:this._removeOption,duplicate:this._duplicateOption,defaultOption:!!this.defaultActions}),this._selected=!0,this._collapsed=!1,this.narrow&&window.setTimeout((()=>{this.scrollIntoView({block:"start",behavior:"smooth"})}),180)}expand(){this.optionsInSidebar?this._collapsed=!1:this.updateComplete.then((()=>{this.shadowRoot.querySelector("ha-expansion-panel").expanded=!0}))}collapse(){this._collapsed=!0}expandAll(){this.expand(),this._conditionElement?.expandAll(),this._actionElement?.expandAll()}collapseAll(){this.collapse(),this._conditionElement?.collapseAll(),this._actionElement?.collapseAll()}_toggleCollapse(){this._collapsed=!this._collapsed}focus(){this._automationRowElement?.focus()}static get styles(){return[y.bH,y.yj,y.Lt,y.aM,s.AH`
        li[role="separator"] {
          border-bottom-color: var(--divider-color);
        }
        h4 {
          color: var(--ha-color-text-secondary);
        }
        h4 {
          margin-bottom: 8px;
        }
        h4.top {
          margin-top: 0;
        }
      `]}constructor(...t){super(...t),this.narrow=!1,this.disabled=!1,this.first=!1,this.last=!1,this.optionsInSidebar=!1,this.sortSelected=!1,this._expanded=!1,this._selected=!1,this._collapsed=!0,this._duplicateOption=()=>{(0,l.r)(this,"duplicate")},this._removeOption=()=>{this.option&&(0,m.dk)(this,{title:this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.delete_confirm_title"),text:this.hass.localize("ui.panel.config.automation.editor.actions.delete_confirm_text"),dismissText:this.hass.localize("ui.common.cancel"),confirmText:this.hass.localize("ui.common.delete"),destructive:!0,confirm:()=>{(0,l.r)(this,"value-changed",{value:null}),this._selected&&(0,l.r)(this,"close-sidebar")}})},this._renameOption=async()=>{const t=await(0,m.an)(this,{title:this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.change_alias"),inputLabel:this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.alias"),inputType:"string",placeholder:(0,p.Z)(this._getDescription()),defaultValue:this.option.alias,confirmText:this.hass.localize("ui.common.submit")});if(null!==t){const e={...this.option};""===t?delete e.alias:e.alias=t,(0,l.r)(this,"value-changed",{value:e})}}}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],H.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],H.prototype,"option",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],H.prototype,"defaultActions",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],H.prototype,"narrow",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],H.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({type:Number})],H.prototype,"index",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],H.prototype,"first",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],H.prototype,"last",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"sidebar"})],H.prototype,"optionsInSidebar",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"sort-selected"})],H.prototype,"sortSelected",void 0),(0,o.__decorate)([(0,n.wk)()],H.prototype,"_expanded",void 0),(0,o.__decorate)([(0,n.wk)()],H.prototype,"_selected",void 0),(0,o.__decorate)([(0,n.wk)()],H.prototype,"_collapsed",void 0),(0,o.__decorate)([(0,n.wk)(),(0,a.Fg)({context:_.ih,subscribe:!0})],H.prototype,"_entityReg",void 0),(0,o.__decorate)([(0,n.P)("ha-automation-condition")],H.prototype,"_conditionElement",void 0),(0,o.__decorate)([(0,n.P)("ha-automation-action")],H.prototype,"_actionElement",void 0),(0,o.__decorate)([(0,n.P)("ha-automation-row")],H.prototype,"_automationRowElement",void 0),H=(0,o.__decorate)([(0,n.EM)("ha-automation-option-row")],H),e()}catch($){e($)}}))},65814:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(69868),a=i(97481),s=i(84922),n=i(11991),r=i(33055),d=i(83490),l=i(73120),c=i(20674),h=i(93360),p=i(76943),u=(i(8115),i(95635),i(68975)),_=i(10611),m=t([p,_]);[p,_]=m.then?(await m)():m;const v="M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z",g="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";class b extends s.WF{render(){return s.qy`
      <ha-sortable
        handle-selector=".handle"
        draggable-selector="ha-automation-option-row"
        .disabled=${this.disabled}
        group="options"
        invert-swap
        @item-moved=${this._optionMoved}
        @item-added=${this._optionAdded}
        @item-removed=${this._optionRemoved}
      >
        <div class="rows ${this.optionsInSidebar?"":"no-sidebar"}">
          ${(0,r.u)(this.options,(t=>this._getKey(t)),((t,e)=>s.qy`
              <ha-automation-option-row
                .sortableData=${t}
                .index=${e}
                .first=${0===e}
                .last=${e===this.options.length-1}
                .option=${t}
                .narrow=${this.narrow}
                .disabled=${this.disabled}
                @duplicate=${this._duplicateOption}
                @move-down=${this._moveDown}
                @move-up=${this._moveUp}
                @value-changed=${this._optionChanged}
                .hass=${this.hass}
                .optionsInSidebar=${this.optionsInSidebar}
                .sortSelected=${this._rowSortSelected===e}
                @stop-sort-selection=${this._stopSortSelection}
              >
                ${this.disabled?s.s6:s.qy`
                      <div
                        tabindex="0"
                        class="handle ${this._rowSortSelected===e?"active":""}"
                        slot="icons"
                        @keydown=${this._handleDragKeydown}
                        @click=${c.d}
                        .index=${e}
                      >
                        <ha-svg-icon .path=${v}></ha-svg-icon>
                      </div>
                    `}
              </ha-automation-option-row>
            `))}
          <div class="buttons">
            <ha-button
              appearance="filled"
              size="small"
              .disabled=${this.disabled}
              @click=${this._addOption}
            >
              <ha-svg-icon .path=${g} slot="start"></ha-svg-icon>
              ${this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.add_option")}
            </ha-button>
            ${this.showDefaultActions?s.s6:s.qy`<ha-button
                  appearance="plain"
                  size="small"
                  .disabled=${this.disabled}
                  @click=${this._showDefaultActions}
                >
                  <ha-svg-icon .path=${g} slot="start"></ha-svg-icon>
                  ${this.hass.localize("ui.panel.config.automation.editor.actions.type.choose.add_default")}
                </ha-button>`}
          </div>
        </div>
      </ha-sortable>
    `}updated(t){if(super.updated(t),t.has("options")&&(this._focusLastOptionOnChange||void 0!==this._focusOptionIndexOnChange)){const t=this._focusLastOptionOnChange?"new":"moved",e=this.shadowRoot.querySelector("ha-automation-option-row:"+("new"===t?"last-of-type":`nth-of-type(${this._focusOptionIndexOnChange+1})`));this._focusLastOptionOnChange=!1,this._focusOptionIndexOnChange=void 0,e.updateComplete.then((()=>{this.narrow&&e.scrollIntoView({block:"start",behavior:"smooth"}),"new"===t&&e.expand(),this.optionsInSidebar?e.openSidebar():e.focus()}))}}expandAll(){this._optionRowElements?.forEach((t=>t.expandAll()))}collapseAll(){this._optionRowElements?.forEach((t=>t.collapseAll()))}_getKey(t){return this._optionsKeys.has(t)||this._optionsKeys.set(t,Math.random().toString()),this._optionsKeys.get(t)}_moveUp(t){t.stopPropagation();const e=t.target.index;if(!t.target.first){const i=e-1;this._move(e,i),this._rowSortSelected===e&&(this._rowSortSelected=i),t.target.focus()}}_moveDown(t){t.stopPropagation();const e=t.target.index;if(!t.target.last){const i=e+1;this._move(e,i),this._rowSortSelected===e&&(this._rowSortSelected=i),t.target.focus()}}_move(t,e){const i=this.options.concat(),o=i.splice(t,1)[0];i.splice(e,0,o),this.options=i,(0,l.r)(this,"value-changed",{value:i})}_optionMoved(t){t.stopPropagation();const{oldIndex:e,newIndex:i}=t.detail;this._move(e,i)}async _optionAdded(t){t.stopPropagation();const{index:e,data:i}=t.detail,o=t.detail.item.selected,a=[...this.options.slice(0,e),i,...this.options.slice(e)];this.options=a,o&&(this._focusOptionIndexOnChange=1===a.length?0:e),await(0,h.E)(),(0,l.r)(this,"value-changed",{value:this.options})}async _optionRemoved(t){t.stopPropagation();const{index:e}=t.detail,i=this.options[e];this.options=this.options.filter((t=>t!==i)),await(0,h.E)();const o=this.options.filter((t=>t!==i));(0,l.r)(this,"value-changed",{value:o})}_optionChanged(t){t.stopPropagation();const e=[...this.options],i=t.detail.value,o=t.target.index;if(null===i)e.splice(o,1);else{const t=this._getKey(e[o]);this._optionsKeys.set(i,t),e[o]=i}(0,l.r)(this,"value-changed",{value:e})}_duplicateOption(t){t.stopPropagation();const e=t.target.index;(0,l.r)(this,"value-changed",{value:this.options.toSpliced(e+1,0,(0,a.A)(this.options[e]))})}_handleDragKeydown(t){"Enter"!==t.key&&" "!==t.key||(t.stopPropagation(),this._rowSortSelected=void 0===this._rowSortSelected?t.target.index:void 0)}_stopSortSelection(){this._rowSortSelected=void 0}constructor(...t){super(...t),this.narrow=!1,this.disabled=!1,this.optionsInSidebar=!1,this.showDefaultActions=!1,this._focusLastOptionOnChange=!1,this._optionsKeys=new WeakMap,this._addOption=()=>{const t=this.options.concat({conditions:[],sequence:[]});this._focusLastOptionOnChange=!0,(0,l.r)(this,"value-changed",{value:t})},this._showDefaultActions=()=>{(0,l.r)(this,"show-default-actions")}}}b.styles=[u.Ju,s.AH`
      :host([root]) .rows {
        padding-inline-end: 8px;
      }
    `],(0,o.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],b.prototype,"narrow",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"options",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"sidebar"})],b.prototype,"optionsInSidebar",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"show-default"})],b.prototype,"showDefaultActions",void 0),(0,o.__decorate)([(0,n.wk)()],b.prototype,"_rowSortSelected",void 0),(0,o.__decorate)([(0,n.wk)(),(0,d.I)({key:"automationClipboard",state:!0,subscribe:!0,storage:"sessionStorage"})],b.prototype,"_clipboard",void 0),(0,o.__decorate)([(0,n.YG)("ha-automation-option-row")],b.prototype,"_optionRowElements",void 0),b=(0,o.__decorate)([(0,n.EM)("ha-automation-option")],b),e()}catch(v){e(v)}}))}};
//# sourceMappingURL=4258.56909f30165ebe17.js.map
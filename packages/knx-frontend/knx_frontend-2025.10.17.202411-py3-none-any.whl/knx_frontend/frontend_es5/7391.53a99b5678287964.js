"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["7391"],{56044:function(e,t,i){i.d(t,{J:function(){return l}});i(79827),i(18223);var a=i(65940),o=i(95075);const l=(0,a.A)((e=>{if(e.time_format===o.Hg.language||e.time_format===o.Hg.system){const t=e.time_format===o.Hg.language?e.language:void 0;return new Date("January 1, 2023 22:00:00").toLocaleString(t).includes("10")}return e.time_format===o.Hg.am_pm}))},36615:function(e,t,i){i(35748),i(92344),i(47849),i(95013);var a=i(69868),o=i(84922),l=i(11991),r=i(13802),s=i(73120),d=i(20674);i(93672),i(20014),i(25223),i(37207),i(11934);let n,h,u,c,p,m,b,y,v,f=e=>e;class _ extends o.WF{render(){return(0,o.qy)(n||(n=f`
      ${0}
      <div class="time-input-wrap-wrap">
        <div class="time-input-wrap">
          ${0}

          <ha-textfield
            id="hour"
            type="number"
            inputmode="numeric"
            .value=${0}
            .label=${0}
            name="hours"
            @change=${0}
            @focusin=${0}
            no-spinner
            .required=${0}
            .autoValidate=${0}
            maxlength="2"
            max=${0}
            min="0"
            .disabled=${0}
            suffix=":"
            class="hasSuffix"
          >
          </ha-textfield>
          <ha-textfield
            id="min"
            type="number"
            inputmode="numeric"
            .value=${0}
            .label=${0}
            @change=${0}
            @focusin=${0}
            name="minutes"
            no-spinner
            .required=${0}
            .autoValidate=${0}
            maxlength="2"
            max="59"
            min="0"
            .disabled=${0}
            .suffix=${0}
            class=${0}
          >
          </ha-textfield>
          ${0}
          ${0}
          ${0}
        </div>

        ${0}
      </div>
      ${0}
    `),this.label?(0,o.qy)(h||(h=f`<label>${0}${0}</label>`),this.label,this.required?" *":""):o.s6,this.enableDay?(0,o.qy)(u||(u=f`
                <ha-textfield
                  id="day"
                  type="number"
                  inputmode="numeric"
                  .value=${0}
                  .label=${0}
                  name="days"
                  @change=${0}
                  @focusin=${0}
                  no-spinner
                  .required=${0}
                  .autoValidate=${0}
                  min="0"
                  .disabled=${0}
                  suffix=":"
                  class="hasSuffix"
                >
                </ha-textfield>
              `),this.days.toFixed(),this.dayLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,this.disabled):o.s6,this.hours.toFixed(),this.hourLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,(0,r.J)(this._hourMax),this.disabled,this._formatValue(this.minutes),this.minLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,this.disabled,this.enableSecond?":":"",this.enableSecond?"has-suffix":"",this.enableSecond?(0,o.qy)(c||(c=f`<ha-textfield
                id="sec"
                type="number"
                inputmode="numeric"
                .value=${0}
                .label=${0}
                @change=${0}
                @focusin=${0}
                name="seconds"
                no-spinner
                .required=${0}
                .autoValidate=${0}
                maxlength="2"
                max="59"
                min="0"
                .disabled=${0}
                .suffix=${0}
                class=${0}
              >
              </ha-textfield>`),this._formatValue(this.seconds),this.secLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,this.disabled,this.enableMillisecond?":":"",this.enableMillisecond?"has-suffix":""):o.s6,this.enableMillisecond?(0,o.qy)(p||(p=f`<ha-textfield
                id="millisec"
                type="number"
                .value=${0}
                .label=${0}
                @change=${0}
                @focusin=${0}
                name="milliseconds"
                no-spinner
                .required=${0}
                .autoValidate=${0}
                maxlength="3"
                max="999"
                min="0"
                .disabled=${0}
              >
              </ha-textfield>`),this._formatValue(this.milliseconds,3),this.millisecLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,this.disabled):o.s6,!this.clearable||this.required||this.disabled?o.s6:(0,o.qy)(m||(m=f`<ha-icon-button
                label="clear"
                @click=${0}
                .path=${0}
              ></ha-icon-button>`),this._clearValue,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"),24===this.format?o.s6:(0,o.qy)(b||(b=f`<ha-select
              .required=${0}
              .value=${0}
              .disabled=${0}
              name="amPm"
              naturalMenuWidth
              fixedMenuPosition
              @selected=${0}
              @closed=${0}
            >
              <ha-list-item value="AM">AM</ha-list-item>
              <ha-list-item value="PM">PM</ha-list-item>
            </ha-select>`),this.required,this.amPm,this.disabled,this._valueChanged,d.d),this.helper?(0,o.qy)(y||(y=f`<ha-input-helper-text .disabled=${0}
            >${0}</ha-input-helper-text
          >`),this.disabled,this.helper):o.s6)}_clearValue(){(0,s.r)(this,"value-changed")}_valueChanged(e){const t=e.currentTarget;this[t.name]="amPm"===t.name?t.value:Number(t.value);const i={hours:this.hours,minutes:this.minutes,seconds:this.seconds,milliseconds:this.milliseconds};this.enableDay&&(i.days=this.days),12===this.format&&(i.amPm=this.amPm),(0,s.r)(this,"value-changed",{value:i})}_onFocus(e){e.currentTarget.select()}_formatValue(e,t=2){return e.toString().padStart(t,"0")}get _hourMax(){if(!this.noHoursLimit)return 12===this.format?12:23}constructor(...e){super(...e),this.autoValidate=!1,this.required=!1,this.format=12,this.disabled=!1,this.days=0,this.hours=0,this.minutes=0,this.seconds=0,this.milliseconds=0,this.dayLabel="",this.hourLabel="",this.minLabel="",this.secLabel="",this.millisecLabel="",this.enableSecond=!1,this.enableMillisecond=!1,this.enableDay=!1,this.noHoursLimit=!1,this.amPm="AM"}}_.styles=(0,o.AH)(v||(v=f`
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
  `)),(0,a.__decorate)([(0,l.MZ)()],_.prototype,"label",void 0),(0,a.__decorate)([(0,l.MZ)()],_.prototype,"helper",void 0),(0,a.__decorate)([(0,l.MZ)({attribute:"auto-validate",type:Boolean})],_.prototype,"autoValidate",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,a.__decorate)([(0,l.MZ)({type:Number})],_.prototype,"format",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],_.prototype,"disabled",void 0),(0,a.__decorate)([(0,l.MZ)({type:Number})],_.prototype,"days",void 0),(0,a.__decorate)([(0,l.MZ)({type:Number})],_.prototype,"hours",void 0),(0,a.__decorate)([(0,l.MZ)({type:Number})],_.prototype,"minutes",void 0),(0,a.__decorate)([(0,l.MZ)({type:Number})],_.prototype,"seconds",void 0),(0,a.__decorate)([(0,l.MZ)({type:Number})],_.prototype,"milliseconds",void 0),(0,a.__decorate)([(0,l.MZ)({type:String,attribute:"day-label"})],_.prototype,"dayLabel",void 0),(0,a.__decorate)([(0,l.MZ)({type:String,attribute:"hour-label"})],_.prototype,"hourLabel",void 0),(0,a.__decorate)([(0,l.MZ)({type:String,attribute:"min-label"})],_.prototype,"minLabel",void 0),(0,a.__decorate)([(0,l.MZ)({type:String,attribute:"sec-label"})],_.prototype,"secLabel",void 0),(0,a.__decorate)([(0,l.MZ)({type:String,attribute:"ms-label"})],_.prototype,"millisecLabel",void 0),(0,a.__decorate)([(0,l.MZ)({attribute:"enable-second",type:Boolean})],_.prototype,"enableSecond",void 0),(0,a.__decorate)([(0,l.MZ)({attribute:"enable-millisecond",type:Boolean})],_.prototype,"enableMillisecond",void 0),(0,a.__decorate)([(0,l.MZ)({attribute:"enable-day",type:Boolean})],_.prototype,"enableDay",void 0),(0,a.__decorate)([(0,l.MZ)({attribute:"no-hours-limit",type:Boolean})],_.prototype,"noHoursLimit",void 0),(0,a.__decorate)([(0,l.MZ)({attribute:!1})],_.prototype,"amPm",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean,reflect:!0})],_.prototype,"clearable",void 0),_=(0,a.__decorate)([(0,l.EM)("ha-base-time-input")],_)},39906:function(e,t,i){i.r(t),i.d(t,{HaTimeSelector:function(){return d}});i(35748),i(95013);var a=i(69868),o=i(84922),l=i(11991);i(243);let r,s=e=>e;class d extends o.WF{render(){var e;return(0,o.qy)(r||(r=s`
      <ha-time-input
        .value=${0}
        .locale=${0}
        .disabled=${0}
        .required=${0}
        clearable
        .helper=${0}
        .label=${0}
        .enableSecond=${0}
      ></ha-time-input>
    `),"string"==typeof this.value?this.value:void 0,this.hass.locale,this.disabled,this.required,this.helper,this.label,!(null!==(e=this.selector.time)&&void 0!==e&&e.no_second))}constructor(...e){super(...e),this.disabled=!1,this.required=!1}}(0,a.__decorate)([(0,l.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,l.MZ)({attribute:!1})],d.prototype,"selector",void 0),(0,a.__decorate)([(0,l.MZ)()],d.prototype,"value",void 0),(0,a.__decorate)([(0,l.MZ)()],d.prototype,"label",void 0),(0,a.__decorate)([(0,l.MZ)()],d.prototype,"helper",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],d.prototype,"disabled",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],d.prototype,"required",void 0),d=(0,a.__decorate)([(0,l.EM)("ha-selector-time")],d)},243:function(e,t,i){i(35748),i(47849),i(95013);var a=i(69868),o=i(84922),l=i(11991),r=i(56044),s=i(73120);i(36615);let d,n=e=>e;class h extends o.WF{render(){const e=(0,r.J)(this.locale);let t=NaN,i=NaN,a=NaN,l=0;if(this.value){var s;const o=(null===(s=this.value)||void 0===s?void 0:s.split(":"))||[];i=o[1]?Number(o[1]):0,a=o[2]?Number(o[2]):0,t=o[0]?Number(o[0]):0,l=t,l&&e&&l>12&&l<24&&(t=l-12),e&&0===l&&(t=12)}return(0,o.qy)(d||(d=n`
      <ha-base-time-input
        .label=${0}
        .hours=${0}
        .minutes=${0}
        .seconds=${0}
        .format=${0}
        .amPm=${0}
        .disabled=${0}
        @value-changed=${0}
        .enableSecond=${0}
        .required=${0}
        .clearable=${0}
        .helper=${0}
        day-label="dd"
        hour-label="hh"
        min-label="mm"
        sec-label="ss"
        ms-label="ms"
      ></ha-base-time-input>
    `),this.label,t,i,a,e?12:24,e&&l>=12?"PM":"AM",this.disabled,this._timeChanged,this.enableSecond,this.required,this.clearable&&void 0!==this.value,this.helper)}_timeChanged(e){e.stopPropagation();const t=e.detail.value,i=(0,r.J)(this.locale);let a;if(!(void 0===t||isNaN(t.hours)&&isNaN(t.minutes)&&isNaN(t.seconds))){let e=t.hours||0;t&&i&&("PM"===t.amPm&&e<12&&(e+=12),"AM"===t.amPm&&12===e&&(e=0)),a=`${e.toString().padStart(2,"0")}:${t.minutes?t.minutes.toString().padStart(2,"0"):"00"}:${t.seconds?t.seconds.toString().padStart(2,"0"):"00"}`}a!==this.value&&(this.value=a,(0,s.r)(this,"change"),(0,s.r)(this,"value-changed",{value:a}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.enableSecond=!1}}(0,a.__decorate)([(0,l.MZ)({attribute:!1})],h.prototype,"locale",void 0),(0,a.__decorate)([(0,l.MZ)()],h.prototype,"value",void 0),(0,a.__decorate)([(0,l.MZ)()],h.prototype,"label",void 0),(0,a.__decorate)([(0,l.MZ)()],h.prototype,"helper",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean,attribute:"enable-second"})],h.prototype,"enableSecond",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean,reflect:!0})],h.prototype,"clearable",void 0),h=(0,a.__decorate)([(0,l.EM)("ha-time-input")],h)}}]);
//# sourceMappingURL=7391.53a99b5678287964.js.map
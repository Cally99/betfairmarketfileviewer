import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: '#263a48',
        secondary: '#2789ce',
        accent: '#8c9eff',
        error: '#b71c1c',
      },
    },
  },
});

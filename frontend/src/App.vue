<template>
  <v-app>
    <v-main>
      <Loader/>
    </v-main>
  </v-app>
</template>

<script>
import Loader from './components/Loader';

export default {
  name: 'App',

  components: {
    Loader,
  },

  data: () => ({
    //
  }),
};
</script>

<template>
  <v-app id="inspire">
    <v-app-bar
      app
      color="#ffb80c"
    >
      <v-container class="py-0 fill-height">
        <v-avatar
          size="32"
        >
          <img src="@/assets/logo.png"/>
        </v-avatar>
        <v-btn
          v-for="link in links"
          :key="link"
          text
        >
          {{ link }}
        </v-btn>
        <v-spacer></v-spacer>
          <h6>powered by <a href="https://github.com/liampauling/betfair">betfairlightweight</a></h6>
      </v-container>
    </v-app-bar>

    <v-main class="grey lighten-3">
      <v-container>
        <v-row>
          <v-col>
            <v-sheet
              min-height="10vh"
              rounded="lg"
            >
              <v-col>
                <v-file-input
                  chips
                  show-size
                  prepend-icon="mdi-card-bulleted"
                  truncate-length="50"
                  label="Select market file (.bz2 or .gz)"
                  :error="error"
                  :error-messages="errorMessage"
                  :loading="loading"
                  @change="onFilePicked"
                ></v-file-input>
              </v-col>
            </v-sheet>
          </v-col>
        </v-row>

        <v-row>
          <v-col>
            <v-sheet
              min-height="40vh"
              rounded="lg"
              v-if="this.marketDefinition"
            >
              <v-col>
                <span v-if="marketDefinition && tab !== null">
                  <v-tabs
                    v-model="tab"
                    align-with-title
                  >
                    <v-tabs-slider></v-tabs-slider>
                    <v-tab
                      v-for="market in marketDefinition"
                      :key="market"
                    >
                      {{ market.eventName }} <br> {{ market.name }}
                    </v-tab>
                  </v-tabs>

                  <v-tabs-items v-model="tab">
                    <v-tab-item
                      v-for="market in marketDefinition"
                      :key="market"
                    >
                      <v-card flat>
                        <v-card-text>
                          <v-col>
                            <h5>{{ market.marketDate }} | {{ market.marketId }} ({{ market.marketType }})</h5>
                          </v-col>
                          <v-col>
                          <v-data-table
                            :headers="headers"
                            :items="market.runners"
                            class="elevation-1"
                            :disable-pagination="true"
                          >
                            <template v-slot:market.runners="{ item }">
                              <v-simple-checkbox
                                v-model="item.enable"
                              ></v-simple-checkbox>
                            </template>
                          </v-data-table>
                          </v-col>
                        </v-card-text>
                      </v-card>
                    </v-tab-item>
                  </v-tabs-items>

                </span>
              </v-col>

              <div class="text-center">
              <v-row>
              <v-col>
                <v-btn
                  v-if="this.marketDefinition"
                  color="primary"
                  :loading="loadingDownload"
                  @click="downloadCSV()"
                >
                  Download csv
                </v-btn>
              </v-col>
              <v-col>

                <v-dialog
                  v-model="dialog"
                  v-if="this.marketDefinition"
                  persistent
                  max-width="800px"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      class="mx-2"
                      fab
                      small
                      plain
                      v-bind="attrs"
                      v-on="on"
                    >
                      download settings
                    </v-btn>

                  </template>
                  <v-card>
                    <v-card-title>
                      <span class="text-h5">Settings</span>
                    </v-card-title>
                    <v-card-text>
                      <v-container>
                        <v-row>
                          <v-col cols="12">
                            <v-combobox
                              v-model="settings.marketColumns"
                              :items="navigation.settings.columns.market"
                              label="Market Columns"
                              color="secondary"
                              multiple
                              chips
                            ></v-combobox>
                          </v-col>
                          <v-col cols="12">
                            <v-combobox
                              v-model="settings.selectionColumns"
                              :items="navigation.settings.columns.selection"
                              label="Selection Columns"
                              color="secondary"
                              multiple
                              chips
                            ></v-combobox>
                          </v-col>

                          <v-col cols="12" sm="6">
                            <v-switch
                              v-model="settings.preplay"
                              label="Preplay"
                              color="secondary"
                              inset
                            ></v-switch>
                          </v-col>
                          <v-col cols="12" sm="6">
                            <v-switch
                              v-model="settings.inplay"
                              label="Inplay"
                              color="secondary"
                              inset
                            ></v-switch>
                          </v-col>

                          <v-col>
                            <v-autocomplete
                              :items="navigation.settings.conflation"
                              label="Conflation*"
                              required
                              v-model="settings.conflation"
                            ></v-autocomplete>
                          </v-col>
                        </v-row>
                      </v-container>
                      <small>*updates in seconds</small>
                    </v-card-text>

                    <v-card-actions>
                      <v-spacer></v-spacer>
                      <v-btn
                        color="blue darken-1"
                        text
                        @click="dialog = false"
                      >
                        save
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-dialog>

                </v-col>
              </v-row>
              </div>
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
  import {HTTP_API} from './http-common';

  export default {
    data: () => ({
      error: false,
      errorMessage: null,
      loading: false,
      loadingDownload: false,
      dialog: false,
      navigation: {},
      headers: [
          {
            text: 'SelectionId',
            align: 'start',
            sortable: false,
            value: 'id',
          },
          { text: 'Name', value: 'name' },
          { text: 'BSP', value: 'bsp' },
          { text: 'Status', value: 'status' }
        ],
      settings: {"conflation": 10, "preplay": true, "inplay": true, "marketColumns": ["marketId", "publishTime"], "selectionColumns": ["selectionId", "lastPriceTraded"]},
      tab: 0,
      file: null,
      marketDefinition: null,
      links: [
        'Betfair Historic Data Processor'
      ],
    }),
    mounted: function() {
      this.getNavigation();
    },
    methods: {
      scrollToTop() {
        window.scrollTo(0,0);
      },

      getNavigation: function() {
        HTTP_API.get('navigation/')
        .then((response) => {
          this.navigation = response.data;
        })
        .catch((err) => {
          console.log(err);
        });
      },

      onFilePicked: function(file) {
        // set loader / reset errors
        this.loading = true;
        this.errorMessage = null;
        this.error = false;
        this.tab = 0,
        this.scrollToTop();
        if (file !== null) {
          // upload file to get marketDefinition
          var formData = new FormData();
          formData.append("file", file);
          HTTP_API.post(
            'file-process/market-definition/',
            formData,
            {headers: {
              'Content-Type': 'multipart/form-data'
            }}
          )
          .then((response) => {
            console.log(response);
            this.marketDefinition = response.data;
            this.file = file;
            this.loading = false;
          })
          .catch((err) => {
            this.errorMessage = 'Error in processing file';
            this.error = true;
            console.log(err);
            this.loading = false;
          });
        } else {
          this.marketDefinition = null;
          this.loading = false;
        }
      },

      downloadCSV: function() {
        this.errorMessage = null;
        this.error = false;
        this.loadingDownload = true;
        var formData = new FormData();
        formData.append("file", this.file);
        let marketId = Object.keys(this.marketDefinition)[this.tab];
        formData.append("marketId", marketId);
        formData.append("inplay", this.settings.inplay);
        formData.append("preplay", this.settings.preplay);
        formData.append("conflation", this.settings.conflation);
        formData.append("marketColumns", this.settings.marketColumns);
        formData.append("selectionColumns", this.settings.selectionColumns);
        HTTP_API.post(
            'file-process/csv/',
            formData,
            {
              headers: {'Content-Type': 'multipart/form-data'},
              responseType: 'blob'
            }
          )
          .then((response) => {
            console.log(response);
            let blob = new Blob([response.data], { type: 'csv' });
            let link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'marketfile.csv';
            link.click();
            this.loadingDownload = false;
          })
          .catch((err) => {
            this.errorMessage = 'Error in processing csv';
            this.error = true;
            console.log(err);
            this.loadingDownload = false;
          });
      }
    }
  }
</script>

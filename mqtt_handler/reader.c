#include "options.h"
#include <cjson/cJSON.h>
#include <curl/curl.h>
#include <curl/easy.h>
#include <curl/typecheck-gcc.h>
#include <mosquitto.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

void post_method(char *message) {
  CURL *curl;
  CURLcode res = curl_global_init(CURL_GLOBAL_ALL);
  struct curl_slist *slist = NULL;
  slist = curl_slist_append(slist, "Content-Type: application/json");

  curl = curl_easy_init();
  if (curl) {
    curl_easy_setopt(curl, CURLOPT_URL, POST_URL);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, slist);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, message);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, (long)strlen(message));

    res = curl_easy_perform(curl);
    if (res != CURLE_OK)
      printf("error! %s\n", curl_easy_strerror(res));
  }

  curl_slist_free_all(slist);
  curl_easy_cleanup(curl);
}

void on_message(struct mosquitto *client, void *idk,
                const struct mosquitto_message *msg) {

  // post_method(msg->payload);
  cJSON *json = cJSON_Parse(msg->payload);
  if (json != NULL) {
    printf("%s\n", cJSON_Print(json));
    post_method(cJSON_Print(json));
  }

  cJSON_Delete(json);
}

int main() {
  mosquitto_lib_init();

  struct mosquitto *client = mosquitto_new(NULL, true, NULL);
  mosquitto_connect(client, BROKER_ADDRESS, BROKER_PORT, 20);

  if (mosquitto_subscribe(client, NULL, "messages", 2) == MOSQ_ERR_SUCCESS) {
    mosquitto_message_callback_set(client, on_message);
    mosquitto_loop_forever(client, 0, 1);
  }

  curl_global_cleanup();
  mosquitto_destroy(client);
  mosquitto_lib_cleanup();
  return 0;
}

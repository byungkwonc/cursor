# @crazydos/nuxt-msw

nuxt-msw integrates MSW (Mock Service Worker) into a Nuxt project, allowing you to use it for API mocking during development. Most of the code can be directly shared with test mocks.

## setup

To install the module to your Nuxt application:

```npm install @crazydos/nuxt-msw msw --save-dev```

```
export default defineNuxtConfig({
  modules: ['@crazydos/nuxt-msw'],
  msw : {
    // Options, see below
  }
})
```

## usage

You need to set up the MSW worker and server separately. When either one is set up, that side will start running. The setup location is in the ```~/msw``` directory (by default), and you configure it through the corresponding files.

### worker
To set up the worker, you need follow the MSW documentation to create a worker file.

```
# For example
npx msw init public --save
```

Next, you need to create a ```worker```.```{ts|js|mjs|cjs}``` file in the ```~/msw``` directory. The worker file will be run in the Nuxt client plugin, which in browser context. Means you can use browser api and Nuxt composable in this file.

```
// ~/msw/worker.ts
import { http, HttpResponse } from 'msw'

export default defineNuxtMswWorkerOption(() => {
  const handlers = [
    // Intercept "GET /api/user" requests...
    http.get('/api/user', () => {
      // ...and respond to them using this JSON response.
      return HttpResponse.json({
        message: "Hello Worker!",
      })
    }),
  ]
  // You can access any browser api
  // window.location.href

  return {
    handlers,
    workerOptions: {
      // ...you can pass options to worker.start()
      // onUnhandledRequest: 'bypass',
    },
    onWorkerStarted(worker, nuxtApp) {
      // Module will setup worker when nuxt run client plugin
      // Means this function will be called after plugin call worker.start()

      nuxtApp.hook('app:mounted', () => {
        // const route = useRoute()
        // console.log(worker.listHandlers())
      })
    },

  }
})
```

You can now try to fetch the data from the worker.

```
<script setup>

onMounted(async () => {
  const res = await $fetch("/api/user")
  console.log(res) // { message: "Hello Worker!" }
})
</script>
```

### server

The way to set up the server is similar to the worker. You need to create a ```server```.```{ts|js|mjs|cjs}``` file in the ```~/msw``` directory.

The server file will be run in Node.js ```Nitro``` context. Because it is before NuxtApp created, you can not access NuxtApp and composable which access it. But you can access msw server and request (h3Event).

One more important thing is that, for your mock and nitro server handler work properly, you need to set baseURL in the server option. The baseURL must be same as your server listening address.

And, when mocking the server side request, you need include the baseURL in your handler's path.

```
// ~/msw/server.ts
import { http, HttpResponse } from 'msw'

export default defineNuxtMswServerOption(() => {
  // assume your server listening at http://localhost:3000
  const baseURL = "http://localhost:3000"

  // composables that not related to NuxtApp can be used here, like: useRuntimeConfig

  const handlers = [
    // Intercept "GET http://localhost:3000/user" requests...
    http.get(baseURL + '/api/user', () => {
      // ...and respond to them using this JSON response.
      return HttpResponse.json({
        message: "Hello msw server!"
      })
    }),
  ]
  return {
    baseURL, // baseURL is required
    handlers,
    serverOptions: {
      onUnhandledRequest: 'bypass',
    },

    onRequest(mswServer, h3Event) {
      // This funtion will be call when Nitro server "request" hook
      console.log('Hello from onRequest')
      mswServer.use(/*...*/)
    },

  }
})
```

After setting up the server, you can now try to fetch the data from the server.

```
<template>
  <h1>{{ data?.message }}</h1>
  <!-- Hello msw server! -->
</template>
<script setup>
const { data, error } = await useFetch('/api/user')
</script>
```

The ```h3Event``` has some basic information about the request, such as event.path. If you need more, you can explicitly install ```h3```, and use it to get more.

```
import { getQuery } from 'h3'

// ...
{
  // ....
  onRequest(mswServer, h3Event) {
    const query = useQuery(h3Event)
    // do something with query
  }
}
```

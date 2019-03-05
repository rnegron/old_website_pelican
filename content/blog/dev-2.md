title: Server-side JavaScript, available in 6 flavors
date: 2019-01-26
slug: server-side-javascript-flavors
category: blog
tags: javascript, node, express, js, backend, programming

I've been reading up on JavaScript these past few months. I feel like there used to be a stigma against the language during my time at university, and maybe there still is. I dug up and read a book I once bought called [JavaScript: The Good Parts](http://shop.oreilly.com/product/9780596517748.do) by Douglas Crockford. It's outdated now, but I used to joke that if "The Good Parts" could be described in 172 pages... Well, suffice it to say, I was not very encouraged.

Well, I've come around. [Modern JavaScript](https://github.com/mbeaudru/modern-js-cheatsheet) is fun to write and, being a web-first language, it entices you to think about problems in a different way from other languages I've tried. After going through some [basic language training](https://developer.mozilla.org/en-US/docs/Web/JavaScript/A_re-introduction_to_JavaScript), it's time to see how to set up a simple web server, JavaScript style.

## A selection of flavors to choose from

Once you start researching your options, you may feel the onset of analysis paralysis. There are a lot of different packages and projects to choose from. I thought it would be fun to write a simple echo server using a few of them, as an excuse to go through their tutorial and docs.

## Setup

Simple as pie. For sending requests, I like to use [HTTPie](https://httpie.org/). We'll use it to easily send some query parameters through `localhost` on port 3000. I should mention that I am running NodeJS v11.7.0 and HTTPie v1.0.2.

## 1) NodeJS Core

First up, vanilla [NodeJS](https://nodejs.org/) style.

```javascript
const http = require("http");
const url = require("url");

const PORT = 3000;

const server = http.createServer((req, res) => {
  res.writeHead(200, { "content-type": "application/json" });

  const query = url.parse(req.url, (parseQueryString = true)).query;

  res.end(JSON.stringify(query));
});

server.listen(PORT, err => {
  if (err) throw err;
  console.log(`Now listening at port ${PORT}...`);
});
```

Testing it out with `http :3000 user==1`, we get the following response:

```bash
HTTP/1.1 200 OK
Connection: keep-alive
Content-Type: application/json
Date: Sat, 26 Jan 2019 22:49:34 GMT
Transfer-Encoding: chunked

{
    "user": "1"
}
```

A nifty, if plain, echo server. We should expect the response from all the servers in this blog post to have the `content-type` header set to "application/json" and the status set at 200, so I will omit the rest of their responses.

Even though the code is quite simple, we still had to work for that echo response. Other packages highlighted in this post will automatically parse the query string from the URL, but we didn't have that luxury here. The response also had to be manually JSON-stringified. Diving a bit deeper (down the prototype chain), we find that our server, from `http.createServer()`, is an [EventEmitter](https://nodejs.org/api/events.html#events_class_eventemitter). It's been instructed to listen for request events at port 3000. The `req` and `res` streams (notice there are two...) represent the client side request and the server side response, respectively. Moving on to the rest of the server-side flavors...

## 2) NodeJS Core: The Sequel

But before that, did you know there is a core NodeJS module called [http2](https://nodejs.org/api/http2.html)? Actually, back it up, did you know there is a [version 2 of HTTP](https://tools.ietf.org/html/rfc7540)?! In any case, this module is a stable part of NodeJS now, so I believe it should get it's own spot.

```javascript
const http2 = require("http2");
const server = http2.createServer();
const url = require("url");

const PORT = 3000;

server.on("error", err => console.error(err));

server.on("stream", (stream, headers) => {
  const response = url.parse(headers[":path"], true).query;

  stream.respond({ ":status": 200, "content-type": "application/json" });

  stream.end(JSON.stringify(response));
});

server.listen(PORT);
console.log(`HTTP2 Server now listening at port ${PORT}...`);
```

We're in it now. Instead of two separate streams, the server now responds to the `stream` event and provides a duplex stream. We obtain the query parameters via the `headers` object, and parse it similarly to how it was done using the original `http` example.

By the way, the above code won't work on browsers... While HTTP/2 [does not](https://http2.github.io/faq/#does-http2-require-encryption) enforce encryption, modern browsers seem to have conspired to enforce it. There exists an `http2.createSecureServer` which can work with browsers. But without setting up a secure server, how will we (taste) test this flavor? Even HTTPie has trouble with it! I tried the experimental [HTTP/2](https://github.com/httpie/httpie-http2) plugin, but could not get it to work.

Let's roll up our sleeves and write a basic HTTP/2 client in Node to get this example to work.

```javascript
const http2 = require("http2");
const PORT = 3000;

const client = http2.connect(`http://localhost:${PORT}`);

client.on("error", err => console.error(err));

const req = client.request({
  ":path": "/?user=1"
});

req.setEncoding("utf8");

let data = [];

req.on("data", chunk => {
  data.push(chunk);
});

req.on("end", () => {
  console.log(data.join());
  client.close();
});

req.end();
```

It works! This flavor we really had to work for, but it was worth it in the end.

(P.S. If you noticed the colon to the left of `"path"` and `"status"` in the code and don't know what they are, may I introduce you to: [pseudo headers](https://http2.github.io/http2-spec/#rfc.section.8.1.2.1))

## 3) Express

Here we have the [Express](https://expressjs.com/) framework, probably the most popular of the NodeJS backend libraries.

```javascript
const express = require("express");
const app = express();
const PORT = 3000;

app.get("/", (req, res) => {
  res.json(req.query);
});

app.listen(PORT, () => {
  console.log(`Express listening on port ${PORT}...`)
});
```

That `app` object has access to a lot more than what is seen here, including a powerful method chaining concept called [middleware](https://expressjs.com/en/guide/using-middleware.html).

## 4) Hapi.js

I had never heard about Hapi before researching this topic. Here's how it looks.

```javascript
const hapi = require("hapi");
const PORT = 3000;

const server = hapi.server({
  host: "localhost",
  port: PORT
});

server.route({
  method: "GET",
  path: "/",
  handler: function(request, headers) {
    return request.query;
  }
});

const startPromise = async function() {
  try {
    await server.start();
  } catch (err) {
    console.error(err);
    process.exit(1);
  }

  console.log(`Hapi running at: ${server.info.uri}`);
};

startPromise();
```

## 5) restify

Probably the least popular of the frameworks in this list. It strives to be a strict implementation of the REST architectural style.

```javascript
const restify = require("restify");
const PORT = 3000;

const server = restify.createServer();
server.use(restify.plugins.queryParser());

server.get("/", (req, res, next) => {
  res.json(req.query);
});

server.listen(PORT, () => {
  console.log(`Restify listening at port ${PORT}`);
});
```

## 6) Koa

Described as a ["next generation framework from the creators of Express"](https://koajs.com/), here's Koa.

```javascript
const koa = require("koa");
const app = new koa();
const PORT = 3000;

app.callback(console.log(`Koa listening on port ${PORT}...`));

app.use(async ctx => {
  ctx.set({ "content-type": "application/json", status: 200 });
  ctx.body = ctx.request.query;
});

app.listen(PORT);
```

From the little time I've spent with all these frameworks, I think I like the look of Koa the most. This was just a very quick look at making a barebones server in all these different packages. Each one has their own ecosystem and quirks, pros and cons. I recommend going through their documentation to see what they can really offer.

Next up, a selection of flavors from the server side of Python frameworks.

Title: Streaming Messages - Anthropic

URL Source: https://docs.anthropic.com/en/api/messages-streaming

Markdown Content:
Streaming Messages - Anthropic
===============
  

    

[Anthropic home page![Image 1: light logo](https://mintlify.s3.us-west-1.amazonaws.com/anthropic/logo/light.svg)![Image 2: dark logo](https://mintlify.s3.us-west-1.amazonaws.com/anthropic/logo/dark.svg)](https://docs.anthropic.com/)

English

Search...

*   [Research](https://www.anthropic.com/research)
*   [News](https://www.anthropic.com/news)
*   [Go to claude.ai](https://claude.ai/)
*   [Go to claude.ai](https://claude.ai/)

Search...

Navigation

Messages

Streaming Messages

[Welcome](https://docs.anthropic.com/en/home)[User Guides](https://docs.anthropic.com/en/docs/welcome)[API Reference](https://docs.anthropic.com/en/api/getting-started)[Prompt Library](https://docs.anthropic.com/en/prompt-library/library)[Release Notes](https://docs.anthropic.com/en/release-notes/overview)[Developer Newsletter](https://docs.anthropic.com/en/developer-newsletter/overview)

*   [Developer Console](https://console.anthropic.com/)
*   [Developer Discord](https://www.anthropic.com/discord)
*   [Support](https://support.anthropic.com/)

##### Using the API

*   [Getting started](https://docs.anthropic.com/en/api/getting-started)
*   [IP addresses](https://docs.anthropic.com/en/api/ip-addresses)
*   [Versions](https://docs.anthropic.com/en/api/versioning)
*   [Errors](https://docs.anthropic.com/en/api/errors)
*   [Rate limits](https://docs.anthropic.com/en/api/rate-limits)
*   [Client SDKs](https://docs.anthropic.com/en/api/client-sdks)
*   [Supported regions](https://docs.anthropic.com/en/api/supported-regions)
*   [Getting help](https://docs.anthropic.com/en/api/getting-help)

##### Anthropic APIs

*   Messages
    
    *   [POST Messages](https://docs.anthropic.com/en/api/messages)
    *   [POST Count Message tokens](https://docs.anthropic.com/en/api/messages-count-tokens)
    *   [Streaming Messages](https://docs.anthropic.com/en/api/messages-streaming)
    *   [Migrating from Text Completions](https://docs.anthropic.com/en/api/migrating-from-text-completions-to-messages)
    *   [Messages examples](https://docs.anthropic.com/en/api/messages-examples)
*   Models
    
*   Message Batches
    
*   Text Completions (Legacy)
    
*   Admin API
    

##### OpenAI SDK compatibility

*   [OpenAI SDK compatibility (beta)](https://docs.anthropic.com/en/api/openai-sdk)

##### Amazon Bedrock API

*   [Amazon Bedrock API](https://docs.anthropic.com/en/api/claude-on-amazon-bedrock)

##### Vertex AI

*   [Vertex AI API](https://docs.anthropic.com/en/api/claude-on-vertex-ai)

Messages

Streaming Messages
==================

When creating a Message, you can set `"stream": true` to incrementally stream the response using [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent%5Fevents/Using%5Fserver-sent%5Fevents) (SSE).

[​](https://docs.anthropic.com/en/api/messages-streaming#streaming-with-sdks)

Streaming with SDKs
----------------------------------------------------------------------------------------------------

Our [Python](https://github.com/anthropics/anthropic-sdk-python) and [TypeScript](https://github.com/anthropics/anthropic-sdk-typescript) SDKs offer multiple ways of streaming. The Python SDK allows both sync and async streams. See the documentation in each SDK for details.

[​](https://docs.anthropic.com/en/api/messages-streaming#event-types)

Event types
------------------------------------------------------------------------------------

Each server-sent event includes a named event type and associated JSON data. Each event will use an SSE event name (e.g. `event: message_stop`), and include the matching event `type` in its data.

Each stream uses the following event flow:

1.  `message_start`: contains a `Message` object with empty `content`.
2.  A series of content blocks, each of which have a `content_block_start`, one or more `content_block_delta` events, and a `content_block_stop` event. Each content block will have an `index` that corresponds to its index in the final Message `content` array.
3.  One or more `message_delta` events, indicating top-level changes to the final `Message` object.
4.  A final `message_stop` event.

### 

[​](https://docs.anthropic.com/en/api/messages-streaming#ping-events)

Ping events

Event streams may also include any number of `ping` events.

### 

[​](https://docs.anthropic.com/en/api/messages-streaming#error-events)

Error events

We may occasionally send [errors](https://docs.anthropic.com/en/api/errors) in the event stream. For example, during periods of high usage, you may receive an `overloaded_error`, which would normally correspond to an HTTP 529 in a non-streaming context:

Example error

```json
event: error
data: {"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}
```

### 

[​](https://docs.anthropic.com/en/api/messages-streaming#other-events)

Other events

In accordance with our [versioning policy](https://docs.anthropic.com/en/api/versioning), we may add new event types, and your code should handle unknown event types gracefully.

[​](https://docs.anthropic.com/en/api/messages-streaming#delta-types)

Delta types
------------------------------------------------------------------------------------

Each `content_block_delta` event contains a `delta` of a type that updates the `content` block at a given `index`.

### 

[​](https://docs.anthropic.com/en/api/messages-streaming#text-delta)

Text delta

A `text` content block delta looks like:

Text delta

```JSON
event: content_block_delta
data: {"type": "content_block_delta","index": 0,"delta": {"type": "text_delta", "text": "ello frien"}}
```

### 

[​](https://docs.anthropic.com/en/api/messages-streaming#input-json-delta)

Input JSON delta

The deltas for `tool_use` content blocks correspond to updates for the `input` field of the block. To support maximum granularity, the deltas are _partial JSON strings_, whereas the final `tool_use.input` is always an _object_.

You can accumulate the string deltas and parse the JSON once you receive a `content_block_stop` event, by using a library like [Pydantic](https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing) to do partial JSON parsing, or by using our [SDKs](https://docs.anthropic.com/en/api/client-sdks), which provide helpers to access parsed incremental values.

A `tool_use` content block delta looks like:

Input JSON delta

```JSON
event: content_block_delta
data: {"type": "content_block_delta","index": 1,"delta": {"type": "input_json_delta","partial_json": "{\"location\": \"San Fra"}}}
```

Note: Our current models only support emitting one complete key and value property from `input` at a time. As such, when using tools, there may be delays between streaming events while the model is working. Once an `input` key and value are accumulated, we emit them as multiple `content_block_delta` events with chunked partial json so that the format can automatically support finer granularity in future models.

### 

[​](https://docs.anthropic.com/en/api/messages-streaming#thinking-delta)

Thinking delta

When using [extended thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking#streaming-extended-thinking) with streaming enabled, you’ll receive thinking content via `thinking_delta` events. These deltas correspond to the `thinking` field of the `thinking` content blocks.

For thinking content, a special `signature_delta` event is sent just before the `content_block_stop` event. This signature is used to verify the integrity of the thinking block.

A typical thinking delta looks like:

Thinking delta

```JSON
event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "Let me solve this step by step:\n\n1. First break down 27 * 453"}}
```

The signature delta looks like:

Signature delta

```JSON
event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "signature_delta", "signature": "EqQBCgIYAhIM1gbcDa9GJwZA2b3hGgxBdjrkzLoky3dl1pkiMOYds..."}}
```

[​](https://docs.anthropic.com/en/api/messages-streaming#raw-http-stream-response)

Raw HTTP Stream response
--------------------------------------------------------------------------------------------------------------

We strongly recommend that use our [client SDKs](https://docs.anthropic.com/en/api/client-sdks) when using streaming mode. However, if you are building a direct API integration, you will need to handle these events yourself.

A stream response is comprised of:

1.  A `message_start` event
2.  Potentially multiple content blocks, each of which contains: a. A `content_block_start` event b. Potentially multiple `content_block_delta` events c. A `content_block_stop` event
3.  A `message_delta` event
4.  A `message_stop` event

There may be `ping` events dispersed throughout the response as well. See [Event types](https://docs.anthropic.com/_sites/docs.anthropic.com/en/api/messages-streaming#event-types) for more details on the format.

### 

[​](https://docs.anthropic.com/en/api/messages-streaming#basic-streaming-request)

Basic streaming request

Request

```bash
curl https://api.anthropic.com/v1/messages \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --data \
'{
  "model": "claude-3-7-sonnet-20250219",
  "messages": [{"role": "user", "content": "Hello"}],
  "max_tokens": 256,
  "stream": true
}'
```

Response

```json
event: message_start
data: {"type": "message_start", "message": {"id": "msg_1nZdL29xx5MUA1yADyHTEsnR8uuvGzszyY", "type": "message", "role": "assistant", "content": [], "model": "claude-3-7-sonnet-20250219", "stop_reason": null, "stop_sequence": null, "usage": {"input_tokens": 25, "output_tokens": 1}}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}

event: ping
data: {"type": "ping"}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "!"}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 0}

event: message_delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence":null}, "usage": {"output_tokens": 15}}

event: message_stop
data: {"type": "message_stop"}

```

### 

[​](https://docs.anthropic.com/en/api/messages-streaming#streaming-request-with-tool-use)

Streaming request with tool use

In this request, we ask Claude to use a tool to tell us the weather.

Request

```bash
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-3-7-sonnet-20250219",
      "max_tokens": 1024,
      "tools": [
        {
          "name": "get_weather",
          "description": "Get the current weather in a given location",
          "input_schema": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA"
              }
            },
            "required": ["location"]
          }
        }
      ],
      "tool_choice": {"type": "any"},
      "messages": [
        {
          "role": "user",
          "content": "What is the weather like in San Francisco?"
        }
      ],
      "stream": true
    }'
```

Response

```json
event: message_start
data: {"type":"message_start","message":{"id":"msg_014p7gG3wDgGV9EUtLvnow3U","type":"message","role":"assistant","model":"claude-3-haiku-20240307","stop_sequence":null,"usage":{"input_tokens":472,"output_tokens":2},"content":[],"stop_reason":null}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: ping
data: {"type": "ping"}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Okay"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":","}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" let"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"'s"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" check"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" the"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" weather"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" for"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" San"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" Francisco"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":","}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" CA"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":":"}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: content_block_start
data: {"type":"content_block_start","index":1,"content_block":{"type":"tool_use","id":"toolu_01T1x1fJ34qAmk2tNTrN7Up6","name":"get_weather","input":{}}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":"{\"location\":"}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":" \"San"}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":" Francisc"}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":"o,"}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":" CA\""}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":", "}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":"\"unit\": \"fah"}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":"renheit\"}"}}

event: content_block_stop
data: {"type":"content_block_stop","index":1}

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"tool_use","stop_sequence":null},"usage":{"output_tokens":89}}

event: message_stop
data: {"type":"message_stop"}
```

### 

[​](https://docs.anthropic.com/en/api/messages-streaming#streaming-request-with-extended-thinking)

Streaming request with extended thinking

In this request, we enable extended thinking with streaming to see Claude’s step-by-step reasoning.

Request

```bash
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-3-7-sonnet-20250219",
    "max_tokens": 20000,
    "stream": true,
    "thinking": {
        "type": "enabled",
        "budget_tokens": 16000
    },
    "messages": [
        {
            "role": "user",
            "content": "What is 27 * 453?"
        }
    ]
}'
```

Response

```json
event: message_start
data: {"type": "message_start", "message": {"id": "msg_01...", "type": "message", "role": "assistant", "content": [], "model": "claude-3-7-sonnet-20250219", "stop_reason": null, "stop_sequence": null}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "thinking", "thinking": ""}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "Let me solve this step by step:\n\n1. First break down 27 * 453"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "\n2. 453 = 400 + 50 + 3"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "\n3. 27 * 400 = 10,800"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "\n4. 27 * 50 = 1,350"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "\n5. 27 * 3 = 81"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "\n6. 10,800 + 1,350 + 81 = 12,231"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "signature_delta", "signature": "EqQBCgIYAhIM1gbcDa9GJwZA2b3hGgxBdjrkzLoky3dl1pkiMOYds..."}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 0}

event: content_block_start
data: {"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "27 * 453 = 12,231"}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 1}

event: message_delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": null}}

event: message_stop
data: {"type": "message_stop"}
```

Was this page helpful?

YesNo

[Count Message tokens](https://docs.anthropic.com/en/api/messages-count-tokens)[Migrating from Text Completions](https://docs.anthropic.com/en/api/migrating-from-text-completions-to-messages)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

On this page

*   [Streaming with SDKs](https://docs.anthropic.com/en/api/messages-streaming#streaming-with-sdks)
*   [Event types](https://docs.anthropic.com/en/api/messages-streaming#event-types)
*   [Ping events](https://docs.anthropic.com/en/api/messages-streaming#ping-events)
*   [Error events](https://docs.anthropic.com/en/api/messages-streaming#error-events)
*   [Other events](https://docs.anthropic.com/en/api/messages-streaming#other-events)
*   [Delta types](https://docs.anthropic.com/en/api/messages-streaming#delta-types)
*   [Text delta](https://docs.anthropic.com/en/api/messages-streaming#text-delta)
*   [Input JSON delta](https://docs.anthropic.com/en/api/messages-streaming#input-json-delta)
*   [Thinking delta](https://docs.anthropic.com/en/api/messages-streaming#thinking-delta)
*   [Raw HTTP Stream response](https://docs.anthropic.com/en/api/messages-streaming#raw-http-stream-response)
*   [Basic streaming request](https://docs.anthropic.com/en/api/messages-streaming#basic-streaming-request)
*   [Streaming request with tool use](https://docs.anthropic.com/en/api/messages-streaming#streaming-request-with-tool-use)
*   [Streaming request with extended thinking](https://docs.anthropic.com/en/api/messages-streaming#streaming-request-with-extended-thinking)

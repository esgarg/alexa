# Play MP3

I often listen to a few MP3s on my phone from a purchased album, the old-school way. So I created a skill to let Alexa play them. The only problem was I could not figure how to store MP3s such that only Alexa can access them. In my case, I uploaded them on s3, gave it public access, tested the skill, but then had to shut it down. If you know of a way, please do suggest. Thanks!

## Intents

* I only created two intents: to list the tracks in case I forget the names and to play the tracks. I did not handle Amazon's pause, resume etc. intents.

## Play Track

* Handling this intent created lots of issues. First was how do you play an audio file, to which Alexa's ssml came to rescue. But only for 90 seconds. Turns out you can only use this for short (< 90s) MP3s. For longer MP3s, you have to use Alexa's streaming directives.

## DialogState

* This created a lot of problems. Firstly it was not there in the JSON I got in the simulator. Turns out it is only seen through the device. I had to check the entire event JSON to see exactly where it was coming.

* It needs a separate response to delgate the dialog to Alexa.

## Conclusion

* Overall its not a bad skill, only if I can figure how to secure my s3 from public access.

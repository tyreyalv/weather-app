# weather-app

A simple application to check Fort Collins weather using the OpenWeatherMap API every 30 mins using argo workflow. If the temperature is above 75 degrees Fahrenheit, the temp_check container will push a notification to my Google Chat channel Weather. It will repeat process until temperature is below 75 degrees Fahrenheit then push another notification. The goal of this project is to learn how to use Argo Workflows, Redis and Google Chat API and how to integrate them together. Its also for keeping my Air Conditionerless house cool during the summer.

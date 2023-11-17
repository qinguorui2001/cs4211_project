# CS4211 Formal Methods for Software Engineering
## Default Project: Applying Probabilistic Model Checking in Sports Analytics
### Introduction:
Traditionally, Probabilistic Model Checking (PMC) was used to analyze the correctness and
performance of computer systems and protocols. However, due to the expressiveness and
generality of PMC’s capabilities, it can be applied in other areas as well. For example, during
the lecture, we demonstrated an interesting case where PMC is applied to tennis analytics to
reason about the relationship between a player's strategy and his winning probabilities. This
example models a tennis singles tiebreaker game. Using this model, we are able to predict
who will win the match and suggest player strategies to improve their chances of winning.
Similarly, we have developed a soccer model to predict the winner in the English Premier
League. We invite you to apply the PMC technique to extend the tennis or soccer model, or
to create a model for a basketball game (NBA). Through this project, we hope you gain
experience in modeling a realistic system using CSP# (PAT).
To help you, we would like to offer the following tips:

• Use proper abstraction to model the states, the state transitions and the player’s
choices. We have provided tennis and soccer models as examples.

• Part of the challenge is to estimate the probabilities in your model. We have
listed data sources and scripts for this purpose.

• Your model will be used to predict the winner of the match. We will provide betting
simulation scripts, so that you can compare your model’s performance with our
example model. You can treat the betting simulation as a sanity check, that is models
with reasonable prediction performance should have similar performance compared
to our example model.

• Disclaimer, please note that the betting simulation is intended exclusively for
evaluating your model's predictive capabilities. This is based on the recognition that
bookmakers are widely recognized for their accurate match result predictions. It is
important to clarify that we do not endorse any illegal betting activities and cannot be
held responsible for any legal repercussions or financial losses resulting from your
engagement in any form of betting.

• One overall project (team) will be awarded a certificate of “Best Project of CS4211”.

### Soccer
Dataset + PAT Model Example:
https://drive.google.com/drive/folders/1Bm_nnJALqkOZdt1MTwQJZORmZAt8xmZs?usp=sharing

A model similar to tennis was done for soccer (the example code for it is heavily
commented). The probabilities for the actions each player can take were taken from the
FIFA video game. Some abstractions were used to simplify the model:
1. Only evaluate one team attacking and defending at any time (2 models for every
match)
2. Fix player positions according to abstracted formations
3. Ball only moves forward
4. Stop trace once intercepted
Potential ideas to extend the existing model:
1. Include more actions that are in the FIFA ratings dataset
2. Change the model structure to something entirely different
Tutor for soccer project: Rajdeep Singh Hundal <rajdeep@u.nus.edu>

#### Group Members:
Name | GithubPage
--- | --- | 
Khor Jun Wei | -
Qin Guo Rui | -
Sun Jun Yang Nicholas | https://github.com/NicsunXnus
Zou Zhixuan | -

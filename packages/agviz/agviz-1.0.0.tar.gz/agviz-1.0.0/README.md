# agviz
AutoGrad Visualizer (agviz): Visualize dependencies between states/parameters in autograd tree.


Unlike related packages (e.g. torvhviz), supports visualizing internal model states and distinguishing states/parameters. Also supports more complex visualization based on traversals of graph and merging nodes.

# Installation:
In the root directory run `pip install -e .`
<br>
You can then install the library in your python code using `from adviz import render' (see Examples)

# Examples:
**examples/gru:** Render the hidden states of a GRU for 5 timesteps, visualizing parameters and states.

![Simple GRU Example](examples/gru/example_ag_viz.png)

<br>

**examples/rnn:** Render the hidden states of a RNN for 5 timesteps, visualizing parameters and states. Also, play with "full" rendering, where we show all the intermediate functions.

![Simple GRU Example](examples/rnn/example_ag_viz.png)

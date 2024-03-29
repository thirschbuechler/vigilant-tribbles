# vigilant-tribbles
cute helper functions which might turn out to be a pain

# how to add?
- `git submodule add https://github.com/thirschbuechler/vigilant-tribbles vigilant_tribbles`
- this results in a git-clone into `vigilant_tribbles` and make a `.gitmodule` section (info for git clients, such as vscode's `git-submodule-assistant`)
- allow executing `chmod +x setup.sh`
- run via `./setup.sh`

# graphics module myink



waterfall             |  make_gif
:-------------------------:|:-------------------------:
![img5](myfigures/waterfall.png "fig1")  |  ![img1](myfigures/test_anim.gif "fig2")

weighted scatter             |  ecke
:-------------------------:|:-------------------------:
![img5](myfigures/weighted_scatter.png "fig3")  |  ![img1](myfigures/ecke.png "fig4")

First of all, a myinkc object needs to be generated, i'll call it pe (plot-element)

- `from vigilant_tribbles.myink import myinkc`
- `pe = myinkc()`

## graph examples
### mpl plot route-throughs
route-throughs for use with helper functions detailed below,
sometimes add extra functionality

- `pe.scatter()`
    adds `weigh`, `weightfactor`
- `pe.stem()`
    adds options for hidestems, hidedots, markersize, markercolor
- `pe.plot()`, `pe.imshow()`, `pe.hist()`
    plain integrations
### new graph types
new graph types built ontop existing ones
- `pe.boxplot()`
    make a boxplot, massaged mpl version
- `pe.stickplot()`
    make a simplified boxplot - "stickplot", just variance and mean
- `pe.stickplot_summary()`
  - make a stickplot and overlay the original datapoints
- `pe.waterfall()`
    make a waterfall-diagram from a matrix, an `imshow` on steroids
- `pe.ecke()`
    make a subplot with a corner in left bot, 5 plots around, e.g.
    corner-booth style with table=biggest_graph, 5 "people" (smaller graphs/images) around
    
also see: [myink_demos.ipynb](myink_demos.ipynb)
## helper function examples
- Figure-related
  - figsizes via `pe.mycanvassize()`
  - cycling through multiple graph-nodes of matplotlib axes after 
    generation via `pe.subplots(nrows=1, ncols=1)`
    - direction control: 
      - after a plot was done, another one can be selected via
    - `pe.onward()` and `pe.backtrack()`
    - no manual fiddling with axs[i] vs ax=axs if only one plot!
    - pe's elements auto-fetch current axis!
- etc
  - `pe.enginerd()` - format a float to engineering notation (returns string)

(Python doc ToDo: sphinx, flake8)
# Marci: Marketing Analytics and ROI Calculator

[![Tests](https://github.com/yourusername/marci/workflows/Tests/badge.svg)](https://github.com/yourusername/marci/actions)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

**Marci** is a comprehensive Python package for marketing analytics, campaign optimization, and ROI calculations. It provides tools for simulating marketing campaigns, analyzing performance, and optimizing budget allocation across multiple channels.

## 🚀 Features

- 🎯 **Campaign Simulation**: Realistic campaign performance modeling with seasonality, conversion delays, and elasticity
- 📊 **Portfolio Optimization**: Multi-campaign budget allocation and performance analysis
- 📈 **Statistical Distributions**: Advanced probability distributions for modeling uncertainty
- 🔄 **Elasticity Analysis**: Marketing mix modeling and response curve analysis
- 📅 **Seasonality Modeling**: Time-series patterns and seasonal adjustments
- ⏱️ **Conversion Delay**: Realistic conversion timing modeling
- 📊 **Visualization**: Built-in plotting and charting capabilities

## 📦 Installation

```bash
pip install marci
```

## 🎯 Quick Start

Marci provides powerful tools for marketing analytics. Let's start with the basics!


## 🔧 Installation and Import

Install the package and import the main classes:



```python
# Standard package import - how users will use it
import marci
from marci import Campaign, Portfolio

# Display available classes
print("✅ Marci package imported successfully!")
print("Available classes:", [attr for attr in dir(marci) if not attr.startswith("_")])

```

    ✅ Marci package imported successfully!
    Available classes: ['Budgets', 'Campaign', 'Conversion_Delay', 'Distribution', 'Elasticity', 'Lognormal', 'PerformanceStats', 'Portfolio', 'Seasonality', 'antidiag_sums', 'budgets', 'campaigns', 'fmt', 'get_campaign_colors', 'portfolio', 'simulated_data', 'style', 'utils']
    

## 🎯 Single Campaign Example

Let's start with a comprehensive single campaign example that demonstrates all the key features of Marci:

### 📋 Campaign Parameters Explained:
- **`name`**: Campaign identifier
- **`start_date`**: Campaign start date
- **`duration`**: Campaign duration in days
- **`budget`**: Total campaign budget
- **`cpm`**: Cost per thousand impressions
- **`cvr`**: Conversion rate (probability of conversion)
- **`aov`**: Average order value
- **`cv`**: Coefficient of variation (volatility)
- **`seasonality_cv`**: Seasonality coefficient of variation
- **`conv_delay`**: Conversion delay probability
- **`conv_delay_duration`**: Conversion delay duration in days
- **`elasticity`**: Marketing elasticity coefficient
- **`is_organic`**: Whether this is an organic campaign



```python
C = Campaign(
    name="Test Campaign",
    start_date="2025-01-01",
    duration=90,
    budget=1000,
    cpm=10,
    cvr=1e-4,
    aov=100,
    cv=0.1,
    seasonality_cv=0.2,
    conv_delay=0.3,
    conv_delay_duration=7,
    elasticity=0.9,
    is_organic=False,
)

# Display campaign statistics
C.print_stats()

# Visualize elasticity and conversion delay effects
C.plot_elasticity_and_delay()

# Plot campaign performance over time
C.plot()

# Access simulation data
print("Simulation DataFrame (first 5 rows):")
print(C.sim_data.df.head())
print("\nAggregated DataFrame (first 5 rows):")
print(C.sim_data.agg_df.head())

```

    Simulating Campaign('Test Campaign', budget=$1,000, duration=90, exp_roas=100%, cv=10%)
    group            meta              budget    sales           roas      
    metric           name       kind     paid     paid    total  paid total
    0       Test Campaign   Expected  $90,000  $90,000  $90,000  100%  100%
    1       Test Campaign  Simulated  $90,617  $97,622  $97,622  108%  108%
    


    
![png](README_files/README_4_1.png)
    



    
![png](README_files/README_4_2.png)
    


    Simulation DataFrame (first 5 rows):
            date           name  seasonality    base       budget  elastic_budget  \
    0 2025-01-01  Test Campaign     1.070570  1000.0  1066.678961        1.066679   
    1 2025-01-02  Test Campaign     0.969624  1000.0  1077.424553        1.077425   
    2 2025-01-03  Test Campaign     0.999554  1000.0   843.474380        0.843474   
    3 2025-01-04  Test Campaign     1.054579  1000.0  1047.619627        1.047620   
    4 2025-01-05  Test Campaign     1.096727  1000.0  1029.258477        1.029258   
    
       elastic_returns      imps  convs        sales  is_organic      roas  
    0         1.059816   96797.0    7.0   649.374062       False  0.608781  
    1         1.069420   88450.0   11.0  1128.692625       False  1.047584  
    2         0.857955   91293.0   11.0  1102.327693       False  1.306889  
    3         1.042757  104047.0   10.0   840.966592       False  0.802740  
    4         1.026295  110951.0   11.0  1477.024418       False  1.435037  
    
    Aggregated DataFrame (first 5 rows):
    Metric                     Budget                     Sales
    Name                Test Campaign          All          All
    date                                                       
    2025-01-01 00:00:00   1066.678961  1066.678961   649.374062
    2025-01-02 00:00:00   1077.424553  1077.424553  1128.692625
    2025-01-03 00:00:00    843.474380   843.474380  1102.327693
    2025-01-04 00:00:00   1047.619627  1047.619627   840.966592
    2025-01-05 00:00:00   1029.258477  1029.258477  1477.024418
    

## 📊 Portfolio Management

Now let's explore portfolio management with multiple campaigns. This example shows how to create and manage a portfolio of campaigns with different characteristics:

### 🏢 Portfolio Campaign Types:
- **Stable Organic**: Low volatility organic campaign
- **High Performance**: High conversion rate paid campaign
- **Low Performance**: Lower conversion rate paid campaign



```python
campaigns = [
    Campaign(
        name="Stable Organic",
        start_date="2025-01-01",
        cv=0,
        seasonality_cv=0,
        duration=90,
        is_organic=True,
    ),
    Campaign(
        name="High Performace",
        cvr=0.0015,
        start_date="2025-02-01",
        duration=20,
    ),
    Campaign(
        name="Low Performance",
        cvr=0.0005,
        start_date="2025-03-01",
        duration=30,
    ),
]

P = Portfolio(campaigns)

# Display portfolio statistics
P.print_stats()

# Visualize portfolio performance
P.plot()

# Access simulation data
print("Portfolio Simulation DataFrame (first 5 rows):")
print(P.sim_data.df.head())
print("\nPortfolio Aggregated DataFrame (first 5 rows):")
print(P.sim_data.agg_df.head())

```

    Budgets('All Budgets', total=$3,000, {'High Performace': $1,000, 'Low Performance': $1,000, 'Stable Organic': $1,000})
    Simulating Campaign('High Performace', budget=$1,000, duration=20, exp_roas=150%, cv=10%)
    Simulating Campaign('Low Performance', budget=$1,000, duration=30, exp_roas=50%, cv=10%)
    Simulating Campaign('Stable Organic', budget=$1,000, duration=90, exp_roas=100%, cv=0%)
    group        meta              budget    sales           roas      
    metric       name       kind     paid     paid     total paid total
    0       Portfolio   Expected  $50,000  $45,000  $135,000  90%  270%
    1       Portfolio  Simulated  $49,271  $44,632  $136,402  91%  277%
    


    
![png](README_files/README_6_1.png)
    


    Portfolio Simulation DataFrame (first 5 rows):
            date            name  seasonality    base       budget  \
    0 2025-01-01  Stable Organic          1.0  1000.0  1000.000565   
    1 2025-01-02  Stable Organic          1.0  1000.0  1000.000427   
    2 2025-01-03  Stable Organic          1.0  1000.0  1000.001450   
    3 2025-01-04  Stable Organic          1.0  1000.0   999.999268   
    4 2025-01-05  Stable Organic          1.0  1000.0   999.999955   
    
       elastic_budget  elastic_returns      imps  convs       sales  is_organic  \
    0        1.000001         1.000000  100382.0   65.0  649.999866        True   
    1        1.000000         1.000000   99524.0   81.0  810.000592        True   
    2        1.000001         1.000001  100650.0   77.0  770.000795        True   
    3        0.999999         0.999999  100233.0   77.0  770.000925        True   
    4        1.000000         1.000000   99475.0   80.0  800.000148        True   
    
           roas  
    0  0.649999  
    1  0.810000  
    2  0.770000  
    3  0.770001  
    4  0.800000  
    
    Portfolio Aggregated DataFrame (first 5 rows):
    Metric                       Budget                                      \
    Name                High Performace Low Performance Stable Organic  All   
    date                                                                      
    2025-01-01 00:00:00             0.0             0.0            0.0  0.0   
    2025-01-02 00:00:00             0.0             0.0            0.0  0.0   
    2025-01-03 00:00:00             0.0             0.0            0.0  0.0   
    2025-01-04 00:00:00             0.0             0.0            0.0  0.0   
    2025-01-05 00:00:00             0.0             0.0            0.0  0.0   
    
    Metric                    Sales  
    Name                        All  
    date                             
    2025-01-01 00:00:00  649.999866  
    2025-01-02 00:00:00  810.000592  
    2025-01-03 00:00:00  770.000795  
    2025-01-04 00:00:00  770.000925  
    2025-01-05 00:00:00  800.000148  
    

## 🎯 Advanced Portfolio Scenarios

This example demonstrates more complex portfolio scenarios with various campaign types and characteristics:

### 📈 Campaign Types in Advanced Portfolio:
- **Noisy Organic Trend**: Organic campaign with seasonal patterns
- **One Time Organic Spike**: Short-duration high-budget organic campaign
- **High Performance Non-Elastic**: High CVR but low elasticity
- **Medium Performance Elastic**: Balanced performance with good elasticity
- **Low Performance Elastic**: Lower CVR but responsive to budget changes



```python
campaigns = [
    Campaign(
        name="Noisy Organic Trend",
        start_date="2025-01-01",
        duration=90,
        budget=2000,
        seasonality_cv=0.3,
        is_organic=True,
    ),
    Campaign(
        name="One Time Organic Spike",
        start_date="2025-02-01",
        duration=3,
        budget=10000,
        seasonality_cv=1,
        conv_delay=0.6,
        conv_delay_duration=28,
        is_organic=True,
    ),
    Campaign(
        name="High Performace Non-Elastic",
        start_date="2025-01-01",
        duration=90,
        budget=1000,
        cvr=0.0015,
        elasticity=0.6,
    ),
    Campaign(
        name="Medium Performace Elastic",
        start_date="2025-01-01",
        duration=90,
        budget=1000,
        cvr=0.001,
        elasticity=0.8,
    ),
    Campaign(
        name="Low Performance Elastic",
        start_date="2025-01-01",
        duration=90,
        budget=1000,
        cvr=0.0005,
        elasticity=0.8,
    ),
]

P = Portfolio(campaigns)

# Display portfolio statistics
P.print_stats()

# Visualize portfolio performance
P.plot()

# Access simulation data
print("Advanced Portfolio Simulation DataFrame (first 5 rows):")
print(P.sim_data.df.head())
print("\nAdvanced Portfolio Aggregated DataFrame (first 5 rows):")
print(P.sim_data.agg_df.head())

```

    Budgets('All Budgets', total=$15,000, {'High Performace Non-Elastic': $1,000, 'Medium Performace Elastic': $1,000, 'Low Performance Elastic': $1,000, 'Noisy Organic Trend': $2,000, 'One Time Organic Spike': $10,000})
    Simulating Campaign('High Performace Non-Elastic', budget=$1,000, duration=90, exp_roas=150%, cv=10%)
    Simulating Campaign('Medium Performace Elastic', budget=$1,000, duration=90, exp_roas=100%, cv=10%)
    Simulating Campaign('Low Performance Elastic', budget=$1,000, duration=90, exp_roas=50%, cv=10%)
    Simulating Campaign('Noisy Organic Trend', budget=$2,000, duration=90, exp_roas=100%, cv=10%)
    Simulating Campaign('One Time Organic Spike', budget=$10,000, duration=3, exp_roas=100%, cv=10%)
    group        meta               budget     sales            roas      
    metric       name       kind      paid      paid     total  paid total
    0       Portfolio   Expected  $270,000  $270,000  $480,000  100%  178%
    1       Portfolio  Simulated  $272,299  $267,292  $470,277   98%  173%
    


    
![png](README_files/README_8_1.png)
    


    Advanced Portfolio Simulation DataFrame (first 5 rows):
            date                         name  seasonality    base       budget  \
    0 2025-01-01  High Performace Non-Elastic     0.702271  1000.0   661.935832   
    1 2025-01-01      Low Performance Elastic     0.931531  1000.0   854.011306   
    2 2025-01-01    Medium Performace Elastic     0.833052  1000.0   636.416261   
    3 2025-01-01          Noisy Organic Trend     0.607796  2000.0  1192.438161   
    4 2025-01-02  High Performace Non-Elastic     0.602950  1000.0   574.981623   
    
       elastic_budget  elastic_returns     imps  convs        sales  is_organic  \
    0        0.661936         0.780710  76205.0   79.0  1020.004479       False   
    1        0.854011         0.881396  97647.0   39.0   361.154190       False   
    2        0.636416         0.696615  78609.0   53.0   526.351551       False   
    3        0.596219         0.661188  98963.0   79.0   846.659166        True   
    4        0.574982         0.717451  59007.0   72.0   704.151962       False   
    
           roas  
    0  1.540942  
    1  0.422892  
    2  0.827055  
    3  0.710024  
    4  1.224651  
    
    Advanced Portfolio Aggregated DataFrame (first 5 rows):
    Metric                                   Budget                          \
    Name                High Performace Non-Elastic Low Performance Elastic   
    date                                                                      
    2025-01-01 00:00:00                  661.935832              854.011306   
    2025-01-02 00:00:00                  574.981623              925.368919   
    2025-01-03 00:00:00                  671.956746             1050.061300   
    2025-01-04 00:00:00                  506.515796              836.507017   
    2025-01-05 00:00:00                  595.779763              850.138304   
    
    Metric                                                             \
    Name                Medium Performace Elastic Noisy Organic Trend   
    date                                                                
    2025-01-01 00:00:00                636.416261                 0.0   
    2025-01-02 00:00:00                823.136665                 0.0   
    2025-01-03 00:00:00                733.582761                 0.0   
    2025-01-04 00:00:00                980.154547                 0.0   
    2025-01-05 00:00:00               1024.326573                 0.0   
    
    Metric                                                         Sales  
    Name                One Time Organic Spike          All          All  
    date                                                                  
    2025-01-01 00:00:00                    0.0  2152.363399  2754.169385  
    2025-01-02 00:00:00                    0.0  2323.487207  2920.950222  
    2025-01-03 00:00:00                    0.0  2455.600807  2676.413372  
    2025-01-04 00:00:00                    0.0  2323.177359  3770.815142  
    2025-01-05 00:00:00                    0.0  2470.244640  3491.831445  
    

## 💰 Budget Optimization

One of Marci's most powerful features is budget optimization. Let's explore how to optimize budget allocation across campaigns:

### 🎯 Optimization Process:
1. **Default Budgets**: Start with current budget allocation
2. **Find Optimal**: Use Marci's optimization algorithm to find the best allocation
3. **Simulate Results**: Run simulations with optimized budgets
4. **Compare Performance**: Analyze the improvement in ROI and sales



```python
# Get default budget allocation
default_budgets = P.budgets
print("Default Budgets:")
print(default_budgets)

# Find optimal budget allocation with $3,000 total budget
optimal_budgets = P.find_optimal_budgets(3000)
print("\nOptimal Budgets (Total: $3,000):")
print(optimal_budgets)

# Simulate outcomes with optimal budgets
P.sim_outcomes(optimal_budgets)

# Display performance statistics with optimized budgets
P.print_stats(optimal_budgets)

# Visualize the optimized portfolio performance
P.plot()

```

    Default Budgets:
    Budgets('Default Budget', total=$3,000, {'High Performace Non-Elastic': $1,000, 'Medium Performace Elastic': $1,000, 'Low Performance Elastic': $1,000})
    
    Optimal Budgets (Total: $3,000):
    Budgets('Optimal Budget', total=$3,000, {'High Performace Non-Elastic': $1,577, 'Medium Performace Elastic': $1,380, 'Low Performance Elastic': $43})
    Budgets('Optimal Budget', total=$15,000, {'High Performace Non-Elastic': $1,577, 'Medium Performace Elastic': $1,380, 'Low Performance Elastic': $43, 'Noisy Organic Trend': $2,000, 'One Time Organic Spike': $10,000})
    Simulating Campaign('High Performace Non-Elastic', budget=$1,000, duration=90, exp_roas=150%, cv=10%)
    Simulating Campaign('Medium Performace Elastic', budget=$1,000, duration=90, exp_roas=100%, cv=10%)
    Simulating Campaign('Low Performance Elastic', budget=$1,000, duration=90, exp_roas=50%, cv=10%)
    Simulating Campaign('Noisy Organic Trend', budget=$2,000, duration=90, exp_roas=100%, cv=10%)
    Simulating Campaign('One Time Organic Spike', budget=$10,000, duration=3, exp_roas=100%, cv=10%)
    Budgets('Optimal Budget', total=$15,000, {'High Performace Non-Elastic': $1,577, 'Medium Performace Elastic': $1,380, 'Low Performance Elastic': $43, 'Noisy Organic Trend': $2,000, 'One Time Organic Spike': $10,000})
    Simulating Campaign('High Performace Non-Elastic', budget=$1,000, duration=90, exp_roas=150%, cv=10%)
    Simulating Campaign('Medium Performace Elastic', budget=$1,000, duration=90, exp_roas=100%, cv=10%)
    

    Simulating Campaign('Low Performance Elastic', budget=$1,000, duration=90, exp_roas=50%, cv=10%)

    
    Simulating Campaign('Noisy Organic Trend', budget=$2,000, duration=90, exp_roas=100%, cv=10%)
    Simulating Campaign('One Time Organic Spike', budget=$10,000, duration=3, exp_roas=100%, cv=10%)
    group        meta               budget     sales            roas      
    metric       name       kind      paid      paid     total  paid total
    0       Portfolio   Expected  $270,000  $297,515  $507,515  110%  188%
    1       Portfolio  Simulated  $270,639  $295,977  $501,271  109%  185%
    


    
![png](README_files/README_10_3.png)
    


## 🚀 High Budget Optimization

Let's explore what happens when we have a much larger budget to work with. This demonstrates how Marci scales with different budget constraints:

### 💡 Key Insights:
- **Elasticity Matters**: Campaigns with higher elasticity get more budget allocation
- **Diminishing Returns**: Some campaigns may receive minimal allocation due to poor performance
- **ROI Optimization**: The algorithm maximizes overall portfolio ROI



```python
# Get default budget allocation
default_budgets = P.budgets
print("Default Budgets:")
print(default_budgets)

# Find optimal budget allocation with $30,000 total budget
optimal_budgets = P.find_optimal_budgets(30000)
print("\nOptimal Budgets (Total: $30,000):")
print(optimal_budgets)

# Simulate outcomes with high budget optimization
P.sim_outcomes(optimal_budgets)

# Display performance statistics with high budget optimization
P.print_stats(optimal_budgets)

# Visualize the high-budget optimized portfolio performance
P.plot()

```

    Default Budgets:
    Budgets('Default Budget', total=$3,000, {'High Performace Non-Elastic': $1,000, 'Medium Performace Elastic': $1,000, 'Low Performance Elastic': $1,000})
    
    Optimal Budgets (Total: $30,000):
    Budgets('Optimal Budget', total=$30,000, {'High Performace Non-Elastic': $6,421, 'Medium Performace Elastic': $22,875, 'Low Performance Elastic': $704})
    Budgets('Optimal Budget', total=$42,000, {'High Performace Non-Elastic': $6,421, 'Medium Performace Elastic': $22,875, 'Low Performance Elastic': $704, 'Noisy Organic Trend': $2,000, 'One Time Organic Spike': $10,000})
    Simulating Campaign('High Performace Non-Elastic', budget=$1,000, duration=90, exp_roas=150%, cv=10%)
    Simulating Campaign('Medium Performace Elastic', budget=$1,000, duration=90, exp_roas=100%, cv=10%)
    Simulating Campaign('Low Performance Elastic', budget=$1,000, duration=90, exp_roas=50%, cv=10%)
    Simulating Campaign('Noisy Organic Trend', budget=$2,000, duration=90, exp_roas=100%, cv=10%)
    Simulating Campaign('One Time Organic Spike', budget=$10,000, duration=3, exp_roas=100%, cv=10%)
    Budgets('Optimal Budget', total=$42,000, {'High Performace Non-Elastic': $6,421, 'Medium Performace Elastic': $22,875, 'Low Performance Elastic': $704, 'Noisy Organic Trend': $2,000, 'One Time Organic Spike': $10,000})
    Simulating Campaign('High Performace Non-Elastic', budget=$1,000, duration=90, exp_roas=150%, cv=10%)
    Simulating Campaign('Medium Performace Elastic', budget=$1,000, duration=90, exp_roas=100%, cv=10%)
    Simulating Campaign('Low Performance Elastic', budget=$1,000, duration=90, exp_roas=50%, cv=10%)
    Simulating Campaign('Noisy Organic Trend', budget=$2,000, duration=90, exp_roas=100%, cv=10%)
    Simulating Campaign('One Time Organic Spike', budget=$10,000, duration=3, exp_roas=100%, cv=10%)
    group        meta                 budget       sales              roas      
    metric       name       kind        paid        paid       total  paid total
    0       Portfolio   Expected    $270,000  $1,546,840  $1,756,840  573%  651%
    1       Portfolio  Simulated  $2,706,257  $1,551,074  $1,768,631   57%   65%
    


    
![png](README_files/README_12_1.png)
    


## 📊 Understanding the Results

### 🎯 Key Metrics Explained:

**Campaign Performance Metrics:**
- **Expected ROAS**: Expected return on ad spend
- **Simulated ROAS**: Actual simulated performance
- **Total Sales**: Combined organic and paid sales
- **Budget Allocation**: How budget is distributed across campaigns

**Portfolio Optimization Insights:**
- **Elasticity Impact**: Higher elasticity campaigns receive more budget
- **Performance Scaling**: Better performing campaigns get priority
- **ROI Maximization**: Algorithm optimizes for maximum overall return

### 📈 Visualization Features:
- **Timeline Plots**: Show performance over time
- **Elasticity Curves**: Demonstrate response to budget changes
- **Conversion Delay**: Show realistic conversion timing
- **Seasonality Patterns**: Display seasonal variations


## 🔧 Advanced Features

### 🎯 Campaign Types and Use Cases:

**Organic Campaigns:**
- Set `is_organic=True`
- No CPM or CVR required
- Can have seasonality and conversion delays
- Represent organic traffic and brand awareness

**Paid Campaigns:**
- Require CPM, CVR, and AOV parameters
- Can have elasticity for budget optimization
- Support various performance characteristics
- Ideal for paid advertising channels

### 📊 Statistical Modeling:

**Uncertainty Modeling:**
- **Coefficient of Variation (CV)**: Controls performance volatility
- **Seasonality CV**: Models seasonal patterns and trends
- **Conversion Delay**: Realistic conversion timing
- **Elasticity**: Response to budget changes

**Distribution Support:**
- Lognormal distributions for realistic performance modeling
- Poisson processes for conversion events
- Beta distributions for conversion rates
- Combined distributions for complex scenarios


## 🚀 Getting Started with Your Own Data

### 📋 Step-by-Step Guide:

1. **Define Your Campaigns:**
   ```python
   campaigns = [
       Campaign(name="Google Ads", cpm=20, cvr=0.001, aov=100, budget=5000),
       Campaign(name="Facebook", cpm=15, cvr=0.0008, aov=80, budget=3000),
       Campaign(name="Organic", is_organic=True, budget=2000),
   ]
   ```

2. **Create Your Portfolio:**
   ```python
   portfolio = Portfolio(campaigns)
   ```

3. **Analyze Performance:**
   ```python
   portfolio.print_stats()
   portfolio.plot()
   ```

4. **Optimize Budgets:**
   ```python
   optimal = portfolio.find_optimal_budgets(10000)
   portfolio.sim_outcomes(optimal)
   ```

### 💡 Pro Tips:
- Start with simple campaigns and gradually add complexity
- Use realistic parameters based on your historical data
- Experiment with different elasticity values
- Consider seasonality for time-sensitive campaigns
- Use conversion delays for more realistic modeling


## 📚 API Reference

### 🎯 Core Classes:

**Campaign:**
- `Campaign(name, start_date, duration, budget, cpm, cvr, aov, cv, seasonality_cv, conv_delay, conv_delay_duration, elasticity, is_organic)`
- `print_stats()`: Display campaign performance statistics
- `plot()`: Visualize campaign performance
- `plot_elasticity_and_delay()`: Show elasticity and conversion delay effects
- `sim_data`: Access simulation data

**Portfolio:**
- `Portfolio(campaigns)`: Create portfolio from list of campaigns
- `print_stats(budgets=None)`: Display portfolio statistics
- `plot()`: Visualize portfolio performance
- `find_optimal_budgets(total_budget)`: Find optimal budget allocation
- `sim_outcomes(budgets=None)`: Run simulations with given budgets
- `sim_data`: Access simulation data

### 📊 Data Structures:

**Simulation Data (`sim_data`):**
- `df`: Detailed daily performance data
- `agg_df`: Aggregated performance metrics

**Budget Objects:**
- `total_budget`: Total budget amount
- `campaign_budgets`: Dictionary of campaign-specific budgets


## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### 🐛 Reporting Issues
If you find a bug or have a feature request, please open an issue on GitHub.

### 📝 Documentation
Help us improve the documentation by submitting pull requests or suggesting improvements.



## 🙏 Acknowledgments

Thanks to all contributors and the open-source community for making this project possible!

---

**Happy Marketing Analytics! 🚀📊**


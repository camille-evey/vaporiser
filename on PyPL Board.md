
The board we use needs to control 4 electrovalves, 2 temperature sensors and one thermostat. 

## main
The main programm on the board has two classes, one to deal with the valves, and one to deal with the pypl board. 

### class Valve

#### constructors

```python 
class Valve(pin)
```
create an object associated with the given pin on the board. 

#### Methods
```python 
Valve.state()
 ```
give a boolean indicating if the valve is open (1) or closed (0)

```python 
Valve.open()
```
set the pin value to 1

```python 
Valve.close()
```
set the pin value to 0

 ```python 
 Valve.toggle()
 ```
Change the value of the pin whatever the state of the valve is

### class PyPL

#### constructors

```python 
class PyPL(cycle=0.01, separators = '\r;', status_cycle=0.1, DEBUG=False)
```
create the board object

#### Methods

``` python 
PyPL.send_temp()
```
send the measured temperature via the COM link. 

```python
PyPL.temp_loop()
```
uses *send_temp* to send temperature measurement every *status-cycle*

```python 
PyPL.loop()
```
Watch and read the serial for instructions

```python 
PyPL.start()
```
initiate and launches the loop


The main program calls three libraries, heartbeat, thermostat, and max31865.

## heartbeat

this one makes a LED (3, the yellow one) shine following the rythm of a heart, in order to make sure the program is working. 

### class Heartbeat

#### constructors

```python 
class Heartbeat(led=3, cycle= 1, on=0.4, max=8, start=True)
```
create the beating led object. 

#### Methods

 ```python
 Heartbeat.loop()
 ```
make the led blink following the rythm and intensity chosen
## max31865

this librarie allows to monitor the PT1000

### class PT1000

#### constructors

```python 
class PT1000(spi, cs_pin, wires=2, refresh=0.25)
```
create the PT1000 object. 

#### Methods

 ```python
 PT1000.spi_write(buf, select = True, deselect = True)
 ```
send data to the buffer

 ```python
 PT1000.spi_read(n=1, select = True, deselect = True)
 ```
recieve data on the bus

 ```python
 PT1000.r2t(raw)
 ```
makes the conversion from the value send by the PT1000 to a celcius (?) temperature

 ```python 
 PT1000.read()
 ```
read the data send from the PT1000 and converts them

```python
PT1000.loop()
```
read the data following an asynchrone timer

```python
PT1000.start()
```
starts the loop

```python
PT1000.stop()
```
cancel all task send previously

## thermostat

Controls the temperature PID

### class _PWM

#### constructors

```python
class _PWM(pin, freq=1)
```
create the PWM object

#### Methods

 ```python
 _PWM.output(p=None)
 ```
returns the pulse width 

```python
_PWM.state()
```
returns the pin value of the PWM

### class PID

#### constructors

```python
class PID(f_in, f_out, set_point = 0, Kp = 3., Ki = 0.01, Kd = 0.0, I_min = -50, I_max = 50, cycle = 1, invert = False)
```
create the PID object. 

#### Methods

```python
PID.update()
```
checks the data and change the values of P, I and D if necessary

```python
PID.loop()
```
makes a loop cycles from update

```python
PID.start()
```
start the loop

```python
PID.stop()
```
stop the loop and resets everything

### class Thermostat

#### constructors

```python
class Thermostat(hot_pid = None, cold_pid = None, T0 = 20)
```
create the Thermostat object. 

#### Methods

```python
Thermostat.start()
```
start the appropriate PID for the T0 chosen

```python
Thermostat.stop()
```
cancel all actions

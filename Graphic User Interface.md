
I used Qt with a custom qss stylesheet (VapoStyle.qss). 
The aim here is to have a very simple interface able to send commands to the board and recieve the data from her. 

### class Fenetre

### constructors

```python
class Fenetre(port=['/dev/tty.usbmodem*', '/dev/ttyACM0', 'COM11'], timeout = 0.1)
```
	create the Fenetre object

### methods

```python
Fenetre.resizeEvent(event=None)
```
	change the size of the background image each time the window changes size

```python 
Fenetre.resizeUi(width=None, height=None)
```
	moves all the widgets each time the window changes size

```python 
Fenetre.send(txt
```
	prints and sends the text to the board via serial

```python 
Fenetre.read(dt)
```
	recieve and analyse the data send by the board

```python
Fenetre.onBtnClicked()
```
	change the state of the valve the user clicked on

```python 
Fenetre.setTemperature()
```
	send the setpoint temperature to the board

```python 
Fenetre.update()
```
	read the temperature in real time

```python
Fenetre.closeEvent(event)
```
	if the window is closed, cancels everything and closes all the valves
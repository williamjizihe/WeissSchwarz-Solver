import tkinter as tk
from tkinter import font as tkfont  # 用于字体设置
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from GameState import Player, atkPlayer, GameState
from ProbabilityTree import ProbabilityTree
# Accurate time measurement
import time
import itertools

DEBUG = False

def calculate():
    # Accurate time measurement
    start_time = time.time()
    deck = (int(entry_deck.get()), int(entry_climax_deck.get()))
    level = (int(entry_level.get()), int(entry_climax_level.get()))
    clock = (int(entry_clock.get()), int(entry_climax_clock.get()))
    waiting_room = (int(entry_waiting_room.get()), int(entry_climax_waiting_room.get()))
    atk = (int(entry_atk.get()), int(entry_atk_soul.get()))
    
    try:
        operator_list = entry_operator_list.get().split(' ')
        operator_list = [op.strip() for op in operator_list]
        operator_list = [op for op in operator_list if op]  # Remove empty strings
        
    except ValueError:
        text_result.delete('1.0', tk.END)
        text_result.insert(tk.END, "Invalid operator list")

    initial_player = Player(deck, waiting_room, level, clock, (0,0))
    initial_atk_player = atkPlayer(atk)
    initial_state = GameState(initial_player, initial_atk_player)
    threshold = 28 - initial_state.hp()  # Auto-calculate threshold
    entry_threshold.delete(0, tk.END)
    entry_threshold.insert(0, str(threshold))  # Display calculated threshold

    probability_tree = ProbabilityTree(initial_state, operator_list)
    probability_tree.build_tree(debug=DEBUG)
    result_dict, kill_prob, expectation, variance = probability_tree.calculate_probabilities(threshold)
    end_time = time.time()
    
    # Update GUI with results
    text_result.delete('1.0', tk.END)
    text_result.insert(tk.END, f"Time taken: {end_time - start_time} seconds\n")
    for damage, prob in result_dict.items():
        text_result.insert(tk.END, f"Damage: {damage}, Probability: {format_result(prob)}\n")
    text_result.insert(tk.END, f"Kill Probability for threshold {threshold}: {format_result(kill_prob)}\n")
    text_result.insert(tk.END, f"Expected Damage: {format_result(expectation)}\n")
    text_result.insert(tk.END, f"Variance: {format_result(variance)}\n")
    
    # Plotting the results
    fig.clear()
    labels = list(result_dict.keys())
    values = list(result_dict.values())
    # 横坐标为间隔为1的整数，纵坐标为对应的概率
    plt.xticks(range(min(labels), max(labels) + 1, 1))
    plt.bar(labels, values, color='blue')
    plt.xlabel('Damage Values')
    plt.ylabel('Probability')
    plt.title('Probability Distribution of Damage Values')
    canvas.draw()

def calculate_best_sequence():
    start_time = time.time()
    deck = (int(entry_deck.get()), int(entry_climax_deck.get()))
    level = (int(entry_level.get()), int(entry_climax_level.get()))
    clock = (int(entry_clock.get()), int(entry_climax_clock.get()))
    waiting_room = (int(entry_waiting_room.get()), int(entry_climax_waiting_room.get()))
    atk = (int(entry_atk.get()), int(entry_atk_soul.get()))

    operator_list = entry_operator_list.get().split()
    operator_list = [op.strip() for op in operator_list if op]  # Remove empty strings and strip

    initial_player = Player(deck, waiting_room, level, clock, (0,0))
    initial_atk_player = atkPlayer(atk)
    initial_state = GameState(initial_player, initial_atk_player)
    threshold = 28 - initial_state.hp()
    entry_threshold.delete(0, tk.END)
    entry_threshold.insert(0, str(threshold))

    sequences = list(itertools.permutations(operator_list))
    # Delete the repeated sequences
    sequences = list(set(sequences))
    results = []

    for seq in sequences:
        probability_tree = ProbabilityTree(initial_state, list(seq))
        probability_tree.build_tree(debug=DEBUG)
        result_dict, kill_prob, expectation, variance = probability_tree.calculate_probabilities(threshold)
        results.append((seq, result_dict, expectation, variance, kill_prob))

    # Sort results by expectation in descending order
    results.sort(key=lambda x: x[2], reverse=True)

    # Update GUI with sorted results
    text_result.delete('1.0', tk.END)
    for seq, _, exp, var, kill_prob in results:
        text_result.insert(tk.END, f"Sequence: {' '.join(seq)}\nExpectation: {format_result(exp)}, Variance: {format_result(var)}, Kill Probability: {format_result(kill_prob)}\n")

    # Plot the results for the top 3 sequences in a combined chart
    fig.clear()
    width = 0.25  # bar width
    min_damage = min(min(res[1].keys()) for res in results[:3])
    max_damage = max(max(res[1].keys()) for res in results[:3])
    damage_indices = {damage: index for index, damage in enumerate(range(min_damage, max_damage + 1), start=0)}
    x = list(damage_indices.values())  # base x coordinates for bars

    ax = fig.add_subplot(111)
    for i, (seq, result_dict, _, _, _) in enumerate(results[:3]):
        # Calculate offsets for each sequence
        offsets = [index - width + i * width for index in x]
        values = [result_dict.get(damage, 0) for damage in range(min_damage, max_damage + 1)]
        ax.bar(offsets, values, width, label=f"Seq {i+1}: {' '.join(seq)}")

    ax.set_xlabel('Damage Values')
    ax.set_ylabel('Probability')
    ax.set_title('Combined Probability Distribution of Damage Values')
    ax.set_xticks(x)
    ax.set_xticklabels([str(dmg) for dmg in range(min_damage, max_damage + 1)])
    ax.legend()

    canvas.draw()

    end_time = time.time()
    text_result.insert(tk.END, f"\nTotal time taken: {end_time - start_time} seconds\n")
    
def format_result(value):
    if display_mode.get() == "Decimal":
        value = float(value)
        # Convert to .xxx format
        return f"{value:.3f}"
    elif display_mode.get() == "Fraction":
        return str(value)  # Convert to fraction
    return value

# Setup main window
root = tk.Tk()
root.title("WS Damage Calculator")

# Set the initial size of the window
root.geometry("1200x800")  # 宽度设置为1200像素，高度设置为800像素

# Font configuration
default_font = tkfont.Font(family="Helvetica", size=12)  # 设置默认字体和大小

# Main layout
left_frame = tk.Frame(root)
left_frame.grid(row=0, column=0, sticky="nsew")
right_frame = tk.Frame(root)
right_frame.grid(row=0, column=1, sticky="nsew")

# Configure grid layout to adjust the column and row weights
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
root.grid_rowconfigure(0, weight=1)

# Setup grid layout, top labels
label_table1 = tk.Label(left_frame, text="Def", font=default_font)
label_table1.grid(row=0, column=0)
label_table2 = tk.Label(left_frame, text="Number of Cards", font=default_font)
label_table2.grid(row=0, column=1)
label_table3 = tk.Label(left_frame, text="Number of Climaxes", font=default_font)
label_table3.grid(row=0, column=2)

# Setup left frame with larger fonts
label_deck = tk.Label(left_frame, text="Deck:", font=default_font)
label_deck.grid(row=1, column=0)
entry_deck = tk.Entry(left_frame, width=10)
entry_deck.grid(row=1, column=1)
entry_climax_deck = tk.Entry(left_frame, width=10)
entry_climax_deck.grid(row=1, column=2)

label_waiting_room = tk.Label(left_frame, text="Waiting Room:", font=default_font)
label_waiting_room.grid(row=2, column=0)
entry_waiting_room = tk.Entry(left_frame, width=10)
entry_waiting_room.insert(0, "0")
entry_waiting_room.grid(row=2, column=1)
entry_climax_waiting_room = tk.Entry(left_frame, width=10)
entry_climax_waiting_room.insert(0, "0")
entry_climax_waiting_room.grid(row=2, column=2)

label_level = tk.Label(left_frame, text="Level:", font=default_font)
label_level.grid(row=3, column=0)
entry_level = tk.Entry(left_frame, width=10)
entry_level.insert(0, "3")
entry_level.grid(row=3, column=1)
entry_climax_level = tk.Entry(left_frame, width=10)
entry_climax_level.insert(0, "0")
entry_climax_level.grid(row=3, column=2)

label_clock = tk.Label(left_frame, text="Clock:", font=default_font)
label_clock.grid(row=4, column=0)
entry_clock = tk.Entry(left_frame, width=10)
entry_clock.insert(0, "0")
entry_clock.grid(row=4, column=1)
entry_climax_clock = tk.Entry(left_frame, width=10)
entry_climax_clock.insert(0, "0")
entry_climax_clock.grid(row=4, column=2)

# Atk
label_table2 = tk.Label(left_frame, text="Number of Cards", font=default_font)
label_table2.grid(row=5, column=1)
label_table3 = tk.Label(left_frame, text="Number of Souls", font=default_font)
label_table3.grid(row=5, column=2)

label_table1 = tk.Label(left_frame, text="Atk", font=default_font)
label_table1.grid(row=6, column=0)

entry_atk = tk.Entry(left_frame, width=10)
entry_atk.grid(row=6, column=1)
entry_atk.insert(0, "21")
entry_atk_soul = tk.Entry(left_frame, width=10)
entry_atk_soul.grid(row=6, column=2)
entry_atk_soul.insert(0, "14")

label_operator_list = tk.Label(left_frame, text="Operator list (space separated):", font=default_font)
label_operator_list.grid(row=7, column=0, columnspan=3)
entry_operator_list = tk.Entry(left_frame, width=30)
entry_operator_list.grid(row=8, column=0, columnspan=3)

# Display Threshold
label_threshold = tk.Label(left_frame, text="Threshold:", font=default_font)
label_threshold.grid(row=9, column=0)
entry_threshold = tk.Entry(left_frame, width=10, font=default_font)
entry_threshold.insert(0, "7")
entry_threshold.grid(row=9, column=1)

# Calculate Button
button_calculate = tk.Button(left_frame, text="Calculate", command=calculate, font=default_font)
button_calculate.grid(row=10, column=0)

# Calculate Best Sequence Button
button_calculate_best_sequence = tk.Button(left_frame, text="Calculate Best Sequence", command=calculate_best_sequence, font=default_font)
button_calculate_best_sequence.grid(row=10, column=1)

# Radio buttons for display mode
display_mode = tk.StringVar(value="Decimal")  # Default display mode
rb_decimal = tk.Radiobutton(left_frame, text="Decimal", variable=display_mode, value="Decimal", font=default_font)
rb_decimal.grid(row=11, column=0, columnspan=2)
rb_fraction = tk.Radiobutton(left_frame, text="Fraction", variable=display_mode, value="Fraction", font=default_font)
rb_fraction.grid(row=11, column=2, columnspan=2)

# Text area for results
text_result = tk.Text(left_frame, height=20, width=80, font=default_font)
text_result.grid(row=12, column=0, columnspan=3)

# Setup right frame for plot
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

root.mainloop()

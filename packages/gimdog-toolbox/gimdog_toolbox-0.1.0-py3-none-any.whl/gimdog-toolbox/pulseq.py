"""
Created in 2025 September

@author: Aron Gimesi (https://github.com/gimesia)
@contact: gimesiaron@gmail.com
"""


import numpy as np
import matplotlib.pyplot as plt
import torch
import pulseq as pp
import MRzeroCore as mr0


# Sequence simulator function
def run_sequence(seq: pp.Sequence, phantom, size, title="Result", plot=True):
    """Run Pulseq sequence on phantom with mr0 simulator and plot results."""
    # D = phantom.D
    # B0 = phantom.B0
    if plot:
        phantom.plot()
    obj_p = phantom.build()
    
    # Write seq file
    seq.write("temp.seq")
    
    # Convert to mr0 sequence object
    mr0_seq = mr0.Sequence.import_file("temp.seq")
    
    # Run Bloch simulation
    graph = mr0.compute_graph(mr0_seq, obj_p, 200, 1e-3)
    signal = mr0.execute_graph(graph, mr0_seq, obj_p, print_progress=False)
    seq.plot(plot_now=False)
    mr0.util.insert_signal_plot(seq=seq, signal=signal.numpy())
    plt.show()

    # ============================================
    #               Plot results
    # ============================================
    if plot:
        fig = plt.figure(figsize=(10,2))

        # Check if we have 2D or 1D data
        expected_2d_size = size[1] * size[0]
        signal_size = signal.numel()
    
        if signal_size == expected_2d_size:
            # 2D k-space data (full imaging sequence)
            kspace_adc = torch.reshape(signal, (size[1], size[0])).clone().t()
            kspace = kspace_adc
            kspace[:,1::2] = torch.flip(kspace[:,1::2],[0])[:,:]
            
            # 2D FFT
            spectrum = torch.fft.fftshift(kspace)
            space = torch.fft.fft2(spectrum)
            space = torch.fft.ifftshift(space)
            
            plt.subplot(141)
            plt.title('k-space')
            mr0.util.imshow(np.abs(kspace.numpy()))
            plt.subplot(142)
            plt.title('log. k-space')
            mr0.util.imshow(np.log(np.abs(kspace.numpy())))
            plt.subplot(143)
            plt.title('FFT-magnitude')
            mr0.util.imshow(np.abs(space.numpy()))
            plt.colorbar()
            plt.subplot(144)
            plt.title('FFT-phase')
            mr0.util.imshow(np.angle(space.numpy()), vmin=-np.pi, vmax=np.pi)
            plt.colorbar()
            
        else:
            # 1D k-space data (FID sequence)
            kspace_1d = signal.clone()
            
            # 1D FFT
            spectrum = torch.fft.fftshift(kspace_1d)
            space = torch.fft.fft(spectrum)
            space = torch.fft.ifftshift(space)
            
            plt.subplot(141)
            plt.title('FID Signal (Real)')
            plt.plot(np.real(kspace_1d.numpy()))
            plt.subplot(142)
            plt.title('FID Signal (Magnitude)')
            plt.plot(np.abs(kspace_1d.numpy()))
            plt.subplot(143)
            plt.title('FFT-magnitude')
            plt.plot(np.abs(space.numpy()))
            plt.subplot(144)
            plt.title('FFT-phase')
            plt.plot(np.angle(space.numpy()))
        
        plt.tight_layout()
        plt.show()
        

def get_event_centers(seq, verbose=True):
    """Get center points of all events in the sequence."""
    cumulative_time = 0
    event_centers = []
    
    for block_idx in range(len(seq.block_events)):
        block = seq.get_block(block_idx + 1)
        block_duration = pp.calc_duration(block)
        
        # Check for RF events
        if hasattr(block, 'rf') and block.rf is not None:
            rf_center = cumulative_time + block_duration / 2
            event_centers.append({
                'type': 'RF',
                'block': block_idx + 1,
                'center': rf_center,
                'use': getattr(block.rf, 'use', 'unknown')
            })
        
        # Check for ADC events
        if hasattr(block, 'adc') and block.adc is not None:
            # ADC center includes delay
            adc_delay = getattr(block.adc, 'delay', 0)
            adc_duration = getattr(block.adc, 'duration', 0)
            adc_center = cumulative_time + adc_delay + adc_duration / 2
            event_centers.append({
                'type': 'ADC',
                'block': block_idx + 1,
                'center': adc_center,
                'delay': adc_delay
            })
        
        cumulative_time += block_duration
    
    if verbose:
        print("Event centers:")
        for event in event_centers:
            print(f"{event['type']} (Block {event['block']}): {event['center']*1000:.3f} ms")
            if event['type'] == 'RF':
                print(f"  Use: {event.get('use', 'unknown')}")
            elif event['type'] == 'ADC':
                print(f"  Delay: {event.get('delay', 0)*1000:.3f} ms")
    
    return event_centers


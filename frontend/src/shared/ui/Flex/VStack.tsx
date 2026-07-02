import {Flex, type FlexProps} from './Flex';

type VStackProps = Omit<FlexProps, 'direction'>;

export function VStack(props: VStackProps) {
  const {align = 'start'} = props;

  return <Flex {...props} align={align} direction="column" />;
}
